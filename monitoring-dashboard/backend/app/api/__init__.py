"""FastAPI application setup and routes"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.utils import get_session
from app.utils.db import TransactionRepository
from app.config import get_settings
from app.schemas import (
    TransactionEventInput,
    TransactionResponse,
    TransactionTraceResponse,
    MetricSnapshot,
    DashboardMetrics,
)
from app.services.event_processor import EventProcessingService
from app.services.metrics import MetricsService
from app.observability import registry, log_event, transactions_total
from app.api.alerts import router as alerts_router
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Monitoring Dashboard API",
    description="Real-time transaction monitoring and alerting system",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts_router)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "monitoring-dashboard-api",
        "timestamp": datetime.utcnow().isoformat(),
    }


# Event Ingestion
@app.post("/api/events", response_model=dict)
async def ingest_event(
    event: TransactionEventInput,
    db: AsyncSession = Depends(get_session),
):
    """Ingest a transaction event"""
    try:
        service = EventProcessingService(db)
        await service.process_event(
            transaction_id=event.transaction_id,
            event_type=event.event_type,
            amount=event.amount,
            provider=event.provider,
            metadata=event.metadata,
            timestamp=event.timestamp,
        )
        transactions_total.inc()
        log_event("event_ingested", {"transaction_id": event.transaction_id})
        return {
            "status": "accepted",
            "transaction_id": event.transaction_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error ingesting event: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Transaction Details
@app.get("/api/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_session),
):
    """Get transaction details"""
    repo = TransactionRepository(db)
    transaction = await repo.get_transaction(transaction_id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return TransactionResponse.model_validate(transaction)


# Transaction Trace
@app.get("/api/transactions/{transaction_id}/trace", response_model=TransactionTraceResponse)
async def get_transaction_trace(
    transaction_id: str,
    db: AsyncSession = Depends(get_session),
):
    """Get full transaction trace"""
    repo = TransactionRepository(db)
    event_repo = TransactionRepository(db)  # Reuse for now
    transaction = await repo.get_transaction(transaction_id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Calculate total processing time
    total_time = 0
    if transaction.events:
        total_time = sum(e.processing_time_ms or 0 for e in transaction.events)

    retry_count = sum(1 for e in transaction.events if "RETRY" in e.event_type)

    return TransactionTraceResponse(
        id=transaction.id,
        transaction_id=transaction.transaction_id,
        reference=transaction.reference,
        current_state=transaction.current_state,
        amount=transaction.amount,
        provider=transaction.provider,
        timeline=[e for e in transaction.events],
        total_processing_time_ms=total_time,
        retry_count=retry_count,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at,
    )


# List Transactions
@app.get("/api/transactions", response_model=list)
async def list_transactions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
):
    """List transactions"""
    repo = TransactionRepository(db)
    transactions = await repo.list_transactions(limit=limit, offset=skip)
    return [TransactionResponse.model_validate(t) for t in transactions]


# Metrics
@app.get("/api/metrics/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(db: AsyncSession = Depends(get_session)):
    """Get complete dashboard metrics"""
    service = MetricsService(db)
    metrics = await service.get_metrics_snapshot()
    state_dist = await service.get_state_distribution()

    return DashboardMetrics(
        timestamp=datetime.utcnow(),
        metrics=metrics,
        health={
            "api": {"service_name": "api", "status": "HEALTHY", "last_heartbeat": datetime.utcnow()},
            "database": {"service_name": "database", "status": "HEALTHY", "last_heartbeat": datetime.utcnow()},
        },
        active_alerts=[],
        total_transactions=0,
        transactions_by_state=state_dist,
    )


# Prometheus metrics endpoint
@app.get("/metrics")
async def get_prometheus_metrics():
    """Export metrics in Prometheus format"""
    return JSONResponse(content=generate_latest(registry).decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Monitoring Dashboard API starting up")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Monitoring Dashboard API shutting down")
