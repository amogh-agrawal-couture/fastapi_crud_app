from redis.asyncio import Redis
from typing import Optional
import os

redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    """Dependency for getting Redis client"""
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client


async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    redis_client = Redis(
        host=redis_host,
        port=redis_port,
        decode_responses=True,
        socket_connect_timeout=5
    )

    try:
        await redis_client.ping()
        print("✓ Redis connected successfully")
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        print("✓ Redis connection closed")