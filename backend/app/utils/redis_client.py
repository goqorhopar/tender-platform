"""Redis client for caching and Celery broker."""

import redis.asyncio as redis
import logging
from typing import Optional, Any
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Async Redis client wrapper."""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        """Initialize Redis connection."""
        if not self._client:
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
            )
            try:
                await self._client.ping()
                logger.info("Connected to Redis successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        if not self._client:
            await self.connect()
        try:
            value = await self._client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in Redis."""
        if not self._client:
            await self.connect()
        try:
            serialized = json.dumps(value)
            if expire:
                return await self._client.setex(key, expire, serialized)
            else:
                return await self._client.set(key, serialized)
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> int:
        """Delete key from Redis."""
        if not self._client:
            await self.connect()
        try:
            return await self._client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self._client:
            await self.connect()
        try:
            return await self._client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get TTL of key in seconds."""
        if not self._client:
            await self.connect()
        try:
            return await self._client.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL for key {key}: {e}")
            return -1
    
    async def publish(self, channel: str, message: str) -> int:
        """Publish message to Redis channel."""
        if not self._client:
            await self.connect()
        try:
            return await self._client.publish(channel, message)
        except Exception as e:
            logger.error(f"Error publishing to channel {channel}: {e}")
            return 0


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Dependency for getting Redis client."""
    if not redis_client._client:
        await redis_client.connect()
    return redis_client
