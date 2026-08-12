"""Redis connection and pub/sub"""

import redis.asyncio as redis
from app.config import get_settings
import logging
import json

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisClient:
    """Redis connection manager"""

    def __init__(self):
        self.client: redis.Redis = None
        self.pubsub: redis.client.PubSub = None

    async def connect(self):
        """Connect to Redis"""
        self.client = await redis.from_url(settings.redis_url)
        logger.info("Connected to Redis")

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis")

    async def publish(self, channel: str, data: dict):
        """Publish message to channel"""
        await self.client.publish(channel, json.dumps(data))
        logger.debug(f"Published to {channel}: {data}")

    async def get(self, key: str):
        """Get value from Redis"""
        value = await self.client.get(key)
        return value.decode() if value else None

    async def set(self, key: str, value: str, ttl: int = None):
        """Set value in Redis"""
        await self.client.set(key, value, ex=ttl)

    async def increment(self, key: str):
        """Increment counter"""
        return await self.client.incr(key)

    async def delete(self, key: str):
        """Delete key"""
        await self.client.delete(key)


# Global Redis client instance
redis_client = RedisClient()


async def get_redis():
    """Dependency for getting Redis client"""
    return redis_client
