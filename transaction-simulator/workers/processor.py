import asyncio
import json
import logging
import random
from datetime import datetime, timezone
from uuid import UUID

from aio_pika.abc import AbstractIncomingMessage

from configs.settings import get_settings
from models.db import SessionLocal, init_db
from models.enums import EventType, TransactionStatus
from observability.logging import configure_logging
from observability.metrics import transaction_processing_latency_seconds, transactions_processed_total
from queues.rabbit import RabbitManager
from services.idempotency import IdempotencyService
from services.transaction_service import TransactionService
from simulator.failure import FailureProfile, FailureSimulator
from workers.common import create_redis

settings = get_settings()
logger = logging.getLogger(__name__)


async def process_message(message: AbstractIncomingMessage, rabbit: RabbitManager, idem: IdempotencyService) -> None:
    payload = json.loads(message.body.decode("utf-8"))
    tx_id = payload["transaction_id"]

    lock_ok = await idem.acquire_processing_lock(tx_id)
    if not lock_ok:
        logger.info("duplicate_processing_blocked", extra={"transaction_id": tx_id})
        await message.ack()
        return

    start = asyncio.get_event_loop().time()

    async with SessionLocal() as session:
        service = TransactionService(session)
        try:
            transaction = await service.get_transaction(UUID(tx_id))
            if transaction is None:
                await message.ack()
                return

            if transaction.status in {TransactionStatus.SETTLED, TransactionStatus.REVERSED}:
                await service.add_event(
                    transaction.id,
                    EventType.DUPLICATE_EVENT.value,
                    {"source": "processor", "payload": payload},
                )
                await session.commit()
                await message.ack()
                return

            await service.update_status(transaction.id, TransactionStatus.PROCESSING)
            await service.add_event(transaction.id, EventType.PROCESSING_STARTED.value, {"at": datetime.now(timezone.utc).isoformat()})
            await session.commit()

            failure_sim = FailureSimulator(
                FailureProfile(
                    success_rate=settings.simulate_success_rate,
                    failure_rate=settings.simulate_failure_rate,
                    timeout_rate=settings.simulate_timeout_rate,
                    delay_rate=settings.simulate_delay_rate,
                    duplicate_rate=settings.simulate_duplicate_rate,
                    provider_unavailable_rate=settings.simulate_provider_unavailable_rate,
                    db_failure_rate=settings.simulate_db_failure_rate,
                )
            )

            if failure_sim.should_delay():
                delay = random.uniform(
                    settings.provider_min_latency_ms / 1000,
                    settings.provider_max_latency_ms / 1000,
                )
                await asyncio.sleep(delay)

            outcome = failure_sim.outcome()
            if outcome == "success":
                await service.update_status(transaction.id, TransactionStatus.AUTHORIZED)
                await service.add_event(transaction.id, EventType.AUTHORIZED.value, {"provider": "sim_provider"})
                await service.update_status(transaction.id, TransactionStatus.SETTLED)
                await service.add_event(transaction.id, EventType.SETTLED.value, {"provider": "sim_provider"})
                await session.commit()
                transactions_processed_total.labels(status="SETTLED").inc()
                await rabbit.publish(
                    settings.queue_processing,
                    {
                        "transaction_id": tx_id,
                        "event": EventType.SETTLED.value,
                        "status": TransactionStatus.SETTLED.value,
                    },
                )
            else:
                new_status = TransactionStatus.TIMEOUT if outcome == "timeout" else TransactionStatus.FAILED
                await service.update_status(transaction.id, new_status)
                await service.add_event(
                    transaction.id,
                    EventType.TIMEOUT.value if outcome == "timeout" else EventType.FAILED.value,
                    {"reason": outcome},
                )
                await session.commit()
                transactions_processed_total.labels(status=new_status.value).inc()

                await rabbit.publish(
                    settings.queue_retry_schedule,
                    {
                        "transaction_id": tx_id,
                        "reason": outcome,
                    },
                )

            latency = asyncio.get_event_loop().time() - start
            transaction_processing_latency_seconds.observe(latency)
            await message.ack()
        except Exception as exc:
            logger.exception("processor_failed", extra={"transaction_id": tx_id, "error": str(exc)})
            await rabbit.publish(settings.queue_retry_schedule, {"transaction_id": tx_id, "reason": "processor_exception"})
            await message.ack()
        finally:
            await idem.release_processing_lock(tx_id)


async def main() -> None:
    configure_logging(settings.log_level)
    await init_db()

    redis = create_redis()
    idem = IdempotencyService(redis)

    rabbit = RabbitManager()
    await rabbit.connect()
    assert rabbit.channel is not None

    queue = rabbit.queues["incoming"]

    logger.info("processor_worker_started")
    async with queue.iterator() as iterator:
        async for message in iterator:
            await process_message(message, rabbit, idem)


if __name__ == "__main__":
    asyncio.run(main())
