"""Event processor worker"""

import asyncio
import json
import logging
from aio_pika import IncomingMessage
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.utils.rabbitmq import rabbitmq_client
from app.utils import get_session_factory
from app.services.event_processor import EventProcessingService
from app.utils.redis import redis_client
from datetime import datetime

logger = logging.getLogger(__name__)
settings = get_settings()


async def process_message(message: IncomingMessage):
    """Process incoming event message"""
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            logger.info(f"Processing event: {data}")

            # Get database session
            factory = get_session_factory()
            async with factory() as db:
                service = EventProcessingService(db)
                await service.process_event(
                    transaction_id=data.get("transaction_id"),
                    event_type=data.get("event_type"),
                    amount=data.get("amount"),
                    provider=data.get("provider"),
                    merchant=data.get("merchant"),
                    metadata=data.get("metadata"),
                    timestamp=datetime.fromisoformat(data.get("timestamp", datetime.utcnow().isoformat())),
                )

            # Publish update to Redis for WebSocket broadcast
            await redis_client.publish(
                "transaction_updates",
                {"transaction_id": data.get("transaction_id"), "event_type": data.get("event_type")},
            )

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)


async def main():
    """Start event processor worker"""
    logger.info("Starting Event Processor Worker")

    # Connect to services
    await rabbitmq_client.connect()
    await redis_client.connect()

    # Start consuming
    await rabbitmq_client.consume_queue("transaction.events", process_message)

    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await rabbitmq_client.disconnect()
        await redis_client.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level)
    asyncio.run(main())
