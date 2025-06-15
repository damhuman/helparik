import redis.asyncio as redis
from typing import Optional, Any, Union
import logging
from functools import wraps
import time

from configuration import REDIS_PASSWORD

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(
        self,
        host: str = "redis",
        port: int = 6379,
        password: str = "password",
        db: int = 0,
        max_retries: int = 3,
        retry_delay: int = 1,
    ):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Establish connection to Redis server."""
        try:
            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=True,
            )
            # Test connection
            await self._client.ping()
            logger.info("Successfully connected to Redis")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def ensure_connection(func):
        """Decorator to ensure Redis connection is established before operations."""

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not self._client:
                await self.connect()
            try:
                return await func(self, *args, **kwargs)
            except redis.ConnectionError:
                # Try to reconnect once
                await self.connect()
                return await func(self, *args, **kwargs)

        return wrapper

    @ensure_connection
    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration."""
        return await self._client.set(key, value, ex=ex)

    @ensure_connection
    async def get(self, key: str) -> Optional[str]:
        """Get value for a key."""
        return await self._client.get(key)

    @ensure_connection
    async def delete(self, key: str) -> int:
        """Delete a key."""
        return await self._client.delete(key)

    @ensure_connection
    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        return bool(await self._client.exists(key))

    @ensure_connection
    async def setex(self, key: str, time: int, value: Any) -> bool:
        """Set a key-value pair with expiration in seconds."""
        return await self._client.setex(key, time, value)

    @ensure_connection
    async def ttl(self, key: str) -> int:
        """Get the time to live for a key in seconds."""
        return await self._client.ttl(key)

    async def close(self) -> None:
        """Close the Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Redis connection closed")


redis_client = RedisClient(password=REDIS_PASSWORD)
