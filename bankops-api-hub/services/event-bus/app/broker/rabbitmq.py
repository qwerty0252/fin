from typing import Any

import aio_pika
from aio_pika import ExchangeType, Message
from aio_pika.abc import AbstractChannel, AbstractRobustConnection

from app.config import Settings
from shared.schemas.events import EventEnvelope
from shared.utils.logging import get_logger

logger = get_logger(__name__)


class RabbitMQBroker:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractChannel | None = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(self._settings.rabbitmq_url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=10)

        # Declare dead-letter exchange
        dlx = await self._channel.declare_exchange(
            self._settings.dead_letter_exchange,
            ExchangeType.DIRECT,
            durable=True,
        )
        dlq = await self._channel.declare_queue(
            self._settings.dead_letter_queue,
            durable=True,
        )
        await dlq.bind(dlx, routing_key=self._settings.dead_letter_queue)

        # Declare main exchange
        await self._channel.declare_exchange(
            self._settings.default_exchange,
            ExchangeType.TOPIC,
            durable=True,
        )

        # Declare standard queues with DLX
        dlx_args: dict[str, Any] = {
            "x-dead-letter-exchange": self._settings.dead_letter_exchange,
            "x-dead-letter-routing-key": self._settings.dead_letter_queue,
            "x-message-ttl": self._settings.retry_delay_ms * self._settings.max_retry_count,
        }
        for queue_name in [
            self._settings.transaction_queue,
            self._settings.notification_queue,
            self._settings.orchestration_queue,
        ]:
            queue = await self._channel.declare_queue(queue_name, durable=True, arguments=dlx_args)
            exchange = await self._channel.get_exchange(self._settings.default_exchange)
            await queue.bind(exchange, routing_key=queue_name)

        logger.info("RabbitMQ broker connected and topology declared")

    async def publish(self, event: EventEnvelope, routing_key: str) -> None:
        if self._channel is None:
            raise RuntimeError("Broker not connected")
        exchange = await self._channel.get_exchange(self._settings.default_exchange)
        message = Message(
            body=event.to_message_body(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            headers={
                "event_type": event.event_type,
                "correlation_id": event.correlation_id,
                "source_service": event.source_service,
                "retry_count": str(event.retry_count),
            },
        )
        await exchange.publish(message, routing_key=routing_key)
        logger.info(
            "event.published",
            event_type=event.event_type,
            event_id=event.event_id,
            routing_key=routing_key,
        )

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
