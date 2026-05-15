import redis.asyncio as redis
import os
from typing import AsyncGenerator

# Redis configuration - using environment variables for Docker compatibility later
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

class RedisManager:
    def __init__(self):
        self.redis_pool = redis.ConnectionPool(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True
        )

    def get_client(self) -> redis.Redis:
        return redis.Redis(connection_pool=self.redis_pool)

# Global manager instance
redis_manager = RedisManager()

# FastAPI Dependency
async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    client = redis_manager.get_client()
    try:
        yield client
    finally:
        await client.close()
