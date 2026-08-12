import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import ReverseRequest, RetryRequest, SimulationRequest, TransactionCreate, TransactionListResponse
from configs.settings import get_settings
from models.db import get_session, init_db
from models.enums import EventType, TransactionStatus
from observability.logging import configure_logging
from observability.metrics import metrics_content_type, metrics_payload, queue_depth
from queues.rabbit import RabbitManager
from services.transaction_service import TransactionService
from simulator.generator import generate_transaction

settings = get_settings()
logger = logging.getLogger(__name__)

rabbit_manager = RabbitManager()
redis_client: Redis | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global redis_client
    configure_logging(settings.log_level)
    await init_db()
    await rabbit_manager.connect()
    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    logger.info("api_started", extra={"service": "transaction-api"})
    try:
        yield
    finally:
        if redis_client:
            await redis_client.close()
        await rabbit_manager.close()


app = FastAPI(title="BankOps Transaction Simulator", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/transactions/simulate")
async def simulate_transactions(
    request: SimulationRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = TransactionService(session)
    created_ids: list[str] = []

    for _ in range(request.count):
        generated = generate_transaction()
        created = await service.create_transaction(
            TransactionCreate(
                reference=generated.reference,
                account_number=generated.account_number,
                amount=generated.amount,
                currency=generated.currency,
                channel=generated.channel,
                transaction_type=generated.transaction_type,
                idempotency_key=generated.idempotency_key,
            )
        )
        payload = {
            "transaction_id": str(created.id),
            "reference": created.reference,
            "idempotency_key": created.idempotency_key,
        }
        await rabbit_manager.publish(settings.queue_incoming, payload)
        created_ids.append(str(created.id))

        if request.duplicates:
            await rabbit_manager.publish(settings.queue_incoming, payload)

    logger.info(
        "transactions_simulated",
        extra={"count": len(created_ids), "duplicates": request.duplicates},
    )
    return {"count": len(created_ids), "transaction_ids": created_ids}


@app.get("/transactions/{transaction_id}")
async def get_transaction(transaction_id: UUID, session: AsyncSession = Depends(get_session)) -> dict:
    service = TransactionService(session)
    transaction = await service.get_transaction(transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {
        "id": str(transaction.id),
        "reference": transaction.reference,
        "amount": float(transaction.amount),
        "currency": transaction.currency,
        "status": transaction.status,
        "channel": transaction.channel,
        "transaction_type": transaction.transaction_type,
        "created_at": transaction.created_at,
        "updated_at": transaction.updated_at,
    }


@app.get("/transactions", response_model=TransactionListResponse)
async def list_transactions(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> TransactionListResponse:
    service = TransactionService(session)
    items, total = await service.list_transactions(limit=limit, offset=offset)
    return TransactionListResponse(items=items, total=total)


@app.post("/transactions/{transaction_id}/retry")
async def retry_transaction(
    transaction_id: UUID,
    request: RetryRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = TransactionService(session)
    tx = await service.get_transaction(transaction_id)
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if tx.status == TransactionStatus.REVERSED and not request.force:
        raise HTTPException(
            status_code=409,
            detail="Transaction is REVERSED. Set force=true to retry anyway.",
        )

    if tx.status == TransactionStatus.SETTLED and not request.force:
        raise HTTPException(
            status_code=409,
            detail="Transaction is SETTLED. Set force=true to retry anyway.",
        )

    reset_applied = False
    if request.reset_retry_count:
        if redis_client is None:
            raise HTTPException(status_code=503, detail="Redis unavailable for retry counter reset")
        await redis_client.delete(f"retry:count:{transaction_id}")
        reset_applied = True

    await service.add_event(
        transaction_id,
        EventType.RETRY_SCHEDULED.value,
        {
            "source": "admin_api",
            "reason": request.reason,
            "reset_retry_count": request.reset_retry_count,
            "immediate": request.immediate,
            "force": request.force,
        },
    )

    if tx.status in {TransactionStatus.FAILED, TransactionStatus.TIMEOUT, TransactionStatus.REVERSED}:
        await service.update_status(transaction_id, TransactionStatus.INITIATED)

    await session.commit()

    target_queue = settings.queue_incoming if request.immediate else settings.queue_retry_schedule
    await rabbit_manager.publish(
        target_queue,
        {"transaction_id": str(transaction_id), "reason": request.reason, "source": "admin_api"},
    )
    return {
        "scheduled": True,
        "transaction_id": str(transaction_id),
        "target_queue": target_queue,
        "reset_retry_count_applied": reset_applied,
    }


@app.post("/transactions/{transaction_id}/reverse")
async def reverse_transaction(
    transaction_id: UUID,
    request: ReverseRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = TransactionService(session)
    tx = await service.get_transaction(transaction_id)
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    await service.add_event(
        transaction_id,
        EventType.REVERSAL_REQUESTED.value,
        {"source": "admin_api", "reason": request.reason},
    )
    await session.commit()

    await rabbit_manager.publish(
        settings.queue_reversal,
        {"transaction_id": str(transaction_id), "reason": request.reason},
    )
    return {"scheduled": True, "transaction_id": str(transaction_id)}


@app.get("/metrics")
async def metrics() -> Response:
    if rabbit_manager.channel:
        for queue_name in [
            settings.queue_incoming,
            settings.queue_processing,
            settings.queue_retry_schedule,
            settings.queue_retry_delay,
            settings.queue_failed,
            settings.queue_reversal,
        ]:
            queue = await rabbit_manager.channel.declare_queue(queue_name, passive=True)
            queue_depth.labels(queue=queue_name).set(queue.declaration_result.message_count)

    return Response(content=metrics_payload(), media_type=metrics_content_type())
