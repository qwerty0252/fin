import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from aio_pika.abc import AbstractIncomingMessage

from configs.settings import get_settings
from models.db import SessionLocal, init_db
from models.enums import EventType
from observability.logging import configure_logging
from observability.metrics import transaction_retries_total
from queues.rabbit import RabbitManager
from retries.policy import RetryPolicy
from services.transaction_service import TransactionService
from workers.common import create_redis, parse_backoff_schedule

settings = get_settings()
logger = logging.getLogger(__name__)


async def process_retry_message(message: AbstractIncomingMessage, rabbit: RabbitManager) -> None:
    payload = json.loads(message.body.decode("utf-8"))
    transaction_id = payload["transaction_id"]
    retry_key = f"retry:count:{transaction_id}"

    redis = create_redis()
    policy = RetryPolicy(parse_backoff_schedule(settings.retry_backoffs_seconds))
    retry_count = await redis.incr(retry_key)

    decision = policy.decide(retry_count - 1)

    async with SessionLocal() as session:
        service = TransactionService(session)
        tx_uuid = UUID(transaction_id)

        if decision.should_retry:
            next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=decision.delay_seconds)
            await service.record_retry(tx_uuid, decision.retry_count, next_retry_at)
            await service.add_event(
                tx_uuid,
                EventType.RETRY_SCHEDULED.value,
                {
                    "retry_count": decision.retry_count,
                    "delay_seconds": decision.delay_seconds,
                    "reason": payload.get("reason", "transient_failure"),
                },
            )
            await session.commit()
            transaction_retries_total.inc()

            await rabbit.publish(
                settings.queue_retry_delay,
                {"transaction_id": transaction_id},
                headers={"retry_count": decision.retry_count},
                expiration_ms=decision.delay_seconds * 1000,
            )
            logger.info(
                "retry_scheduled",
                extra={"transaction_id": transaction_id, "retry_count": decision.retry_count},
            )
        else:
            await service.add_event(
                tx_uuid,
                EventType.RETRY_EXHAUSTED.value,
                {"retry_count": retry_count, "reason": "retry_limit_exceeded"},
            )
            await session.commit()

            await rabbit.publish(
                settings.queue_failed,
                {"transaction_id": transaction_id, "reason": "retry_limit_exceeded"},
            )
            await rabbit.publish(
                settings.queue_reversal,
                {
                    "transaction_id": transaction_id,
                    "reason": "exceeded_retry_threshold",
                },
            )
            logger.info("retry_exhausted", extra={"transaction_id": transaction_id})

    await redis.close()
    await message.ack()


async def main() -> None:
    configure_logging(settings.log_level)
    await init_db()
    rabbit = RabbitManager()
    await rabbit.connect()
    assert rabbit.channel is not None

    queue = rabbit.queues["retry_schedule"]

    logger.info("retry_worker_started")
    async with queue.iterator() as iterator:
        async for message in iterator:
            await process_retry_message(message, rabbit)


if __name__ == "__main__":
    asyncio.run(main())
