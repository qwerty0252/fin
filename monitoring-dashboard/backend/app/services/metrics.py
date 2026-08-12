"""Metrics aggregation service"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.models import Transaction, TransactionStateEnum, TransactionEvent
from app.schemas import MetricSnapshot
from app.observability import (
    active_transactions,
    transactions_total,
    transactions_failed_total,
)
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MetricsService:
    """Service for aggregating and calculating metrics"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_metrics_snapshot(self) -> MetricSnapshot:
        """Get current metrics snapshot"""
        now = datetime.utcnow()
        last_minute = now - timedelta(minutes=1)
        last_hour = now - timedelta(hours=1)

        # Count transactions by state
        result = await self.db.execute(
            select(Transaction.current_state, func.count(Transaction.id)).group_by(
                Transaction.current_state
            )
        )
        state_counts = dict(result.all())

        # Active transactions (not in terminal states)
        active_count = sum(
            count
            for state, count in state_counts.items()
            if state not in [
                TransactionStateEnum.SETTLED,
                TransactionStateEnum.FAILED,
                TransactionStateEnum.REVERSED,
                TransactionStateEnum.REFUNDED,
                TransactionStateEnum.TIMEOUT,
            ]
        )

        # Total transactions
        result = await self.db.execute(select(func.count(Transaction.id)))
        total_transactions = result.scalar() or 0

        # Failed transactions
        result = await self.db.execute(
            select(func.count(Transaction.id)).where(Transaction.current_state == TransactionStateEnum.FAILED)
        )
        failed_count = result.scalar() or 0

        # Transactions in last minute
        result = await self.db.execute(
            select(func.count(Transaction.id)).where(Transaction.created_at >= last_minute)
        )
        minute_count = result.scalar() or 0

        # Transactions in last hour
        result = await self.db.execute(
            select(func.count(Transaction.id)).where(Transaction.created_at >= last_hour)
        )
        hour_count = result.scalar() or 0

        # Calculate latencies
        result = await self.db.execute(
            select(func.avg(TransactionEvent.processing_time_ms)).where(
                TransactionEvent.timestamp >= last_minute
            )
        )
        avg_latency = result.scalar() or 0

        # Calculate percentiles (simplified - using direct calculation)
        result = await self.db.execute(
            select(TransactionEvent.processing_time_ms)
            .where(TransactionEvent.timestamp >= last_minute)
            .order_by(TransactionEvent.processing_time_ms)
        )
        latencies = [row[0] for row in result.fetchall() if row[0]]

        p95_latency = self._calculate_percentile(latencies, 95) if latencies else 0
        p99_latency = self._calculate_percentile(latencies, 99) if latencies else 0

        # Update prometheus metrics
        active_transactions.set(active_count)

        # Calculate rates
        success_count = total_transactions - failed_count
        success_rate = (success_count / total_transactions * 100) if total_transactions > 0 else 0
        failure_rate = (failed_count / total_transactions * 100) if total_transactions > 0 else 0

        return MetricSnapshot(
            tps=minute_count / 60.0,  # TPS over last minute
            rpm=hour_count / 60.0,  # RPM over last hour
            success_rate=success_rate,
            failure_rate=failure_rate,
            avg_latency_ms=float(avg_latency),
            p95_latency_ms=float(p95_latency),
            p99_latency_ms=float(p99_latency),
            active_transactions=active_count,
            queue_depth=0,  # Will be updated by queue monitoring
            retry_queue_depth=0,  # Will be updated by queue monitoring
            connected_clients=0,  # Will be updated by WebSocket gateway
        )

    @staticmethod
    def _calculate_percentile(values: list, percentile: int) -> float:
        """Calculate percentile from list of values"""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return float(sorted_values[min(index, len(sorted_values) - 1)])

    async def get_state_distribution(self) -> dict:
        """Get transaction count by state"""
        result = await self.db.execute(
            select(Transaction.current_state, func.count(Transaction.id)).group_by(
                Transaction.current_state
            )
        )
        return {str(state): count for state, count in result.all()}
