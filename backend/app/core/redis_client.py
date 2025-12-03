"""
Redis client initialization and connection management.
"""
import redis
from redis import Redis
from app.core.config import settings
from app.utils.logger import logger


class RedisClient:
    """Singleton Redis client wrapper."""
    
    _instance: Redis | None = None
    
    @classmethod
    def get_client(cls) -> Redis:
        """Get or create Redis client instance."""
        if cls._instance is None:
            try:
                cls._instance = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Test connection
                cls._instance.ping()
                logger.info(f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            except redis.ConnectionError as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        return cls._instance
    
    @classmethod
    def close(cls) -> None:
        """Close Redis connection."""
        if cls._instance:
            cls._instance.close()
            cls._instance = None
            logger.info("Redis connection closed")


def get_redis() -> Redis:
    """Dependency function to get Redis client."""
    return RedisClient.get_client()
