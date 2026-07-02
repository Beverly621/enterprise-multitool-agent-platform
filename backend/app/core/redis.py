from functools import lru_cache

from app.core.config import settings
from redis import Redis


@lru_cache
def get_redis_client() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)

