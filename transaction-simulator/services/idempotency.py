from redis.asyncio import Redis

from configs.settings import get_settings

settings = get_settings()


class IdempotencyService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def acquire_processing_lock(self, transaction_id: str) -> bool:
        key = f"lock:transaction:{transaction_id}"
        return await self.redis.set(key, "1", ex=settings.retry_lock_ttl_seconds, nx=True) is True

    async def release_processing_lock(self, transaction_id: str) -> None:
        key = f"lock:transaction:{transaction_id}"
        await self.redis.delete(key)

    async def mark_processed(self, idempotency_key: str) -> None:
        key = f"idempotency:{idempotency_key}"
        await self.redis.set(key, "1", ex=settings.idempotency_ttl_seconds)

    async def is_processed(self, idempotency_key: str) -> bool:
        key = f"idempotency:{idempotency_key}"
        value = await self.redis.get(key)
        return value is not None
