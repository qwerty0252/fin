import json
from typing import Any

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractExchange

from configs.settings import get_settings

settings = get_settings()


class RabbitManager:
    def __init__(self, url: str | None = None):
        self.url = url or settings.rabbitmq_url
        self.connection: AbstractConnection | None = None
        self.channel: AbstractChannel | None = None
        self.exchange: AbstractExchange | None = None
        self.queues: dict = {}

    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=100)
        self.exchange = await self.channel.declare_exchange(
            settings.rabbit_exchange,
            ExchangeType.TOPIC,
            durable=True,
        )
        await self._declare_topology()

    async def close(self) -> None:
        if self.channel and not self.channel.is_closed:
            await self.channel.close()
        if self.connection and not self.connection.is_closed:
            await self.connection.close()

    async def _declare_topology(self) -> None:
        if not self.channel or not self.exchange:
            raise RuntimeError("RabbitMQ channel not initialized")

        self.queues["incoming"] = await self.channel.declare_queue(
            settings.queue_incoming,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.rabbit_exchange,
                "x-dead-letter-routing-key": settings.queue_failed,
            },
        )
        self.queues["processing"] = await self.channel.declare_queue(settings.queue_processing, durable=True)
        self.queues["retry_schedule"] = await self.channel.declare_queue(settings.queue_retry_schedule, durable=True)
        self.queues["retry_delay"] = await self.channel.declare_queue(
            settings.queue_retry_delay,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.rabbit_exchange,
                "x-dead-letter-routing-key": settings.queue_incoming,
            },
        )
        self.queues["failed"] = await self.channel.declare_queue(settings.queue_failed, durable=True)
        self.queues["reversal"] = await self.channel.declare_queue(settings.queue_reversal, durable=True)

        await self.queues["incoming"].bind(self.exchange, routing_key=settings.queue_incoming)
        await self.queues["processing"].bind(self.exchange, routing_key=settings.queue_processing)
        await self.queues["retry_schedule"].bind(self.exchange, routing_key=settings.queue_retry_schedule)
        await self.queues["retry_delay"].bind(self.exchange, routing_key=settings.queue_retry_delay)
        await self.queues["failed"].bind(self.exchange, routing_key=settings.queue_failed)
        await self.queues["reversal"].bind(self.exchange, routing_key=settings.queue_reversal)

    async def publish(
        self,
        routing_key: str,
        payload: dict[str, Any],
        headers: dict[str, Any] | None = None,
        expiration_ms: int | None = None,
    ) -> None:
        if not self.exchange:
            raise RuntimeError("RabbitMQ exchange is not initialized")
        message = Message(
            json.dumps(payload).encode("utf-8"),
            content_type="application/json",
            headers=headers or {},
            delivery_mode=DeliveryMode.PERSISTENT,
            expiration=expiration_ms,
        )
        await self.exchange.publish(message, routing_key=routing_key)
