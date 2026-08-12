"""RabbitMQ connection and message handling"""

import aio_pika
from aio_pika import Channel, Connection, Exchange, Queue
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class RabbitMQClient:
    """RabbitMQ connection manager"""

    def __init__(self):
        self.connection: Connection = None
        self.channel: Channel = None
        self.exchanges: dict = {}
        self.queues: dict = {}

    async def connect(self):
        """Connect to RabbitMQ"""
        self.connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        self.channel = await self.connection.channel()
        logger.info("Connected to RabbitMQ")

    async def disconnect(self):
        """Disconnect from RabbitMQ"""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")

    async def get_exchange(self, name: str, durable: bool = True):
        """Get or create exchange"""
        if name not in self.exchanges:
            self.exchanges[name] = await self.channel.declare_exchange(
                name=name,
                type=aio_pika.ExchangeType.DIRECT,
                durable=durable,
            )
        return self.exchanges[name]

    async def get_queue(self, name: str, durable: bool = True):
        """Get or create queue"""
        if name not in self.queues:
            self.queues[name] = await self.channel.declare_queue(
                name=name,
                durable=durable,
            )
        return self.queues[name]

    async def publish_event(self, exchange_name: str, routing_key: str, message: dict):
        """Publish message to exchange"""
        import json

        exchange = await self.get_exchange(exchange_name)
        msg = aio_pika.Message(
            body=json.dumps(message).encode(),
            content_type="application/json",
        )
        await exchange.publish(msg, routing_key=routing_key)
        logger.debug(f"Published to {exchange_name}/{routing_key}: {message}")

    async def consume_queue(self, queue_name: str, callback):
        """Start consuming from queue"""
        queue = await self.get_queue(queue_name)
        await queue.consume(callback)
        logger.info(f"Started consuming from {queue_name}")


# Global RabbitMQ client instance
rabbitmq_client = RabbitMQClient()
