import redis.asyncio as redis

from app.config import RedisConfig


def create_redis() -> redis.Redis:
    pool = redis.ConnectionPool.from_url(RedisConfig.REDIS_URL())
    return redis.Redis.from_pool(pool)
