import asyncio
import json
import logging
from uuid import UUID

from aio_pika.abc import AbstractIncomingMessage

from configs.settings import get_settings
from models.db import SessionLocal, init_db
from models.enums import EventType, TransactionStatus
from observability.logging import configure_logging
from observability.metrics import transaction_reversals_total
from queues.rabbit import RabbitManager
from services.transaction_service import TransactionService
from workers.common import create_redis

settings = get_settings()
logger = logging.getLogger(__name__)


async def process_reversal_message(message: AbstractIncomingMessage) -> None:
    payload = json.loads(message.body.decode("utf-8"))
    tx_id = payload["transaction_id"]
    reason = payload.get("reason", "auto_reversal")

    redis = create_redis()
    reversal_lock_key = f"lock:reversal:{tx_id}"
    lock_ok = await redis.set(reversal_lock_key, "1", ex=300, nx=True)
    if not lock_ok:
        await redis.close()
        await message.ack()
        return

    async with SessionLocal() as session:
        service = TransactionService(session)
        transaction = await service.get_transaction(UUID(tx_id))
        if transaction is None:
            await redis.close()
            await message.ack()
            return

        if transaction.status == TransactionStatus.REVERSED:
            await redis.close()
            await message.ack()
            return

        await service.record_reversal(UUID(tx_id), reason, status="COMPLETED")
        await service.update_status(UUID(tx_id), TransactionStatus.REVERSED)
        await service.add_event(UUID(tx_id), EventType.REVERSED.value, {"reason": reason})
        await session.commit()
        transaction_reversals_total.inc()

        logger.info("transaction_reversed", extra={"transaction_id": tx_id, "reason": reason})

    await redis.close()
    await message.ack()


async def main() -> None:
    configure_logging(settings.log_level)
    await init_db()
    rabbit = RabbitManager()
    await rabbit.connect()
    assert rabbit.channel is not None

    queue = rabbit.queues["reversal"]

    logger.info("reversal_worker_started")
    async with queue.iterator() as iterator:
        async for message in iterator:
            await process_reversal_message(message)


if __name__ == "__main__":
    asyncio.run(main())
