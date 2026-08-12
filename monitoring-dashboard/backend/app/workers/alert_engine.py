"""Alert engine for monitoring dashboard"""

import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import Alert, AlertSeverityEnum, Transaction, TransactionStateEnum
from app.utils.db import get_session_factory
from app.services.metrics import MetricsService
from app.utils.redis import redis_client
import json

logger = logging.getLogger(__name__)


class AlertEngine:
    """Engine for evaluating alert rules and triggering alerts"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.metrics_service = MetricsService(db)

    async def evaluate_rules(self):
        """Evaluate all alert rules"""
        try:
            metrics = await self.metrics_service.get_metrics_snapshot()
            
            # Rule 1: High failure rate
            if metrics.failure_rate > 10:
                await self.trigger_alert(
                    severity=AlertSeverityEnum.CRITICAL,
                    alert_type="HIGH_FAILURE_RATE",
                    message=f"Failure rate is {metrics.failure_rate:.1f}% (threshold: 10%)",
                )

            # Rule 2: High latency
            if metrics.p95_latency_ms > 5000:
                await self.trigger_alert(
                    severity=AlertSeverityEnum.WARNING,
                    alert_type="HIGH_LATENCY",
                    message=f"P95 latency is {metrics.p95_latency_ms:.0f}ms (threshold: 5000ms)",
                )

            # Rule 3: Queue congestion
            if metrics.queue_depth > 1000:
                await self.trigger_alert(
                    severity=AlertSeverityEnum.WARNING,
                    alert_type="QUEUE_CONGESTION",
                    message=f"Queue depth is {metrics.queue_depth} (threshold: 1000)",
                )

            # Rule 4: Retry queue backlog
            if metrics.retry_queue_depth > 500:
                await self.trigger_alert(
                    severity=AlertSeverityEnum.WARNING,
                    alert_type="RETRY_BACKLOG",
                    message=f"Retry queue depth is {metrics.retry_queue_depth} (threshold: 500)",
                )

        except Exception as e:
            logger.error(f"Error evaluating alert rules: {str(e)}")

    async def trigger_alert(
        self,
        severity: AlertSeverityEnum,
        alert_type: str,
        message: str,
        metadata: dict = None,
    ) -> Alert:
        """Trigger an alert"""
        
        # Check for existing active alert of same type
        result = await self.db.execute(
            select(Alert).where(
                and_(
                    Alert.alert_type == alert_type,
                    Alert.status == "ACTIVE",
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.debug(f"Alert {alert_type} already active, skipping duplicate")
            return existing

        # Create new alert
        alert = Alert(
            severity=severity,
            alert_type=alert_type,
            message=message,
            status="ACTIVE",
            extra_data=metadata,
        )
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)

        logger.warning(f"Alert triggered: {alert_type} - {message}")

        # Publish to Redis for real-time notification
        await redis_client.publish(
            "alert_triggered",
            {
                "alert_id": alert.id,
                "severity": severity.value,
                "alert_type": alert_type,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        return alert

    async def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        result = await self.db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        
        if alert:
            alert.status = "RESOLVED"
            alert.resolved_at = datetime.utcnow()
            await self.db.commit()
            
            logger.info(f"Alert resolved: {alert.alert_type}")

            # Publish resolution
            await redis_client.publish(
                "alert_resolved",
                {
                    "alert_id": alert.id,
                    "alert_type": alert.alert_type,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )


async def alert_engine_loop():
    """Continuous alert evaluation loop"""
    logger.info("Starting Alert Engine")

    factory = get_session_factory()
    
    while True:
        try:
            async with factory() as db:
                engine = AlertEngine(db)
                await engine.evaluate_rules()
        except Exception as e:
            logger.error(f"Error in alert engine loop: {str(e)}")

        # Evaluate rules every 30 seconds
        await asyncio.sleep(30)


async def main():
    """Start alert engine"""
    await redis_client.connect()
    await alert_engine_loop()


if __name__ == "__main__":
    import logging.config

    logging.basicConfig(level="INFO")
    asyncio.run(main())
