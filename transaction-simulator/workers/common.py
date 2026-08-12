from redis.asyncio import Redis

from configs.settings import get_settings

settings = get_settings()


def create_redis() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


def parse_backoff_schedule(raw_schedule: str) -> list[int]:
    return [int(v.strip()) for v in raw_schedule.split(",") if v.strip()]
