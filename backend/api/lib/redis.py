"""Redis client singleton with connection pooling"""
import redis
from redis import ConnectionPool, Redis
from typing import Optional
import logging
from api.config import settings

logger = logging.getLogger(__name__)

# Global Redis connection pool
_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[Redis] = None


def get_redis_client() -> Optional[Redis]:
    """
    Get Redis client singleton instance.
    Returns None if Redis is unavailable (graceful degradation).
    """
    global _redis_client, _redis_pool

    if _redis_client is not None:
        return _redis_client

    try:
        # Create connection pool
        _redis_pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=50,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            retry_on_timeout=True,
        )

        # Create Redis client
        _redis_client = Redis(connection_pool=_redis_pool)

        # Test connection
        _redis_client.ping()
        logger.info(f"Redis client initialized successfully: {settings.redis_url}")
        return _redis_client

    except Exception as e:
        logger.warning(f"Redis unavailable: {e}. Continuing without Redis (graceful degradation).")
        _redis_client = None
        _redis_pool = None
        return None


def is_redis_available() -> bool:
    """Check if Redis is available and healthy"""
    client = get_redis_client()
    if client is None:
        return False

    try:
        client.ping()
        return True
    except Exception:
        return False


def close_redis_connection():
    """Close Redis connection pool (for cleanup)"""
    global _redis_client, _redis_pool

    if _redis_client:
        try:
            _redis_client.close()
        except Exception as e:
            logger.error(f"Error closing Redis client: {e}")

    if _redis_pool:
        try:
            _redis_pool.disconnect()
        except Exception as e:
            logger.error(f"Error closing Redis pool: {e}")

    _redis_client = None
    _redis_pool = None

