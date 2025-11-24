"""Response caching middleware using Redis"""
import json
import hashlib
from typing import Optional, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
import logging
from api.lib.redis import get_redis_client

logger = logging.getLogger(__name__)

# Default TTL in seconds
DEFAULT_TTL = 3600  # 1 hour


def generate_cache_key(request: Request, include_query: bool = True) -> str:
    """Generate cache key from request path and query params"""
    key_parts = [request.method, request.url.path]

    if include_query and request.query_params:
        # Sort query params for consistent keys
        sorted_params = sorted(request.query_params.items())
        query_string = "&".join(f"{k}={v}" for k, v in sorted_params)
        key_parts.append(query_string)

    key_string = ":".join(key_parts)
    # Create hash for long keys
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return f"cache:{key_hash}"


class CacheMiddleware(BaseHTTPMiddleware):
    """
    Middleware to cache GET request responses in Redis.
    Only caches successful responses (200 OK).
    """

    def __init__(
        self,
        app,
        ttl: int = DEFAULT_TTL,
        cache_paths: Optional[list] = None,
        exclude_paths: Optional[list] = None,
    ):
        super().__init__(app)
        self.ttl = ttl
        # Paths to cache (if None, cache all GET requests)
        self.cache_paths = cache_paths or []
        # Paths to exclude from caching
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json"]

    async def dispatch(self, request: Request, call_next: Callable):
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)

        # Check if path should be excluded
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Check if path should be cached
        if self.cache_paths and not any(
            request.url.path.startswith(path) for path in self.cache_paths
        ):
            return await call_next(request)

        # Try to get from cache
        redis_client = get_redis_client()
        if redis_client:
            cache_key = generate_cache_key(request)
            try:
                cached_response = redis_client.get(cache_key)
                if cached_response:
                    logger.debug(f"Cache hit: {cache_key}")
                    return Response(
                        content=cached_response,
                        media_type="application/json",
                        headers={"X-Cache": "HIT"},
                    )
            except Exception as e:
                logger.warning(f"Cache read error: {e}")

        # Execute request
        response = await call_next(request)

        # Cache successful responses
        if redis_client and response.status_code == 200:
            cache_key = generate_cache_key(request)
            try:
                # Read response body
                if isinstance(response, StreamingResponse):
                    body = b""
                    async for chunk in response.body_iterator:
                        body += chunk
                    response_body = body
                else:
                    response_body = response.body

                # Store in cache
                redis_client.setex(cache_key, self.ttl, response_body)
                logger.debug(f"Cache set: {cache_key} (TTL: {self.ttl}s)")

                # Return response with cache header
                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    media_type=response.media_type,
                    headers={**dict(response.headers), "X-Cache": "MISS"},
                )
            except Exception as e:
                logger.warning(f"Cache write error: {e}")

        return response


def invalidate_cache_pattern(pattern: str):
    """
    Invalidate cache entries matching a pattern.
    Pattern examples: 'cache:projects:*', 'cache:project:123'
    """
    redis_client = get_redis_client()
    if not redis_client:
        return

    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache entries matching: {pattern}")
    except Exception as e:
        logger.warning(f"Cache invalidation error: {e}")


def invalidate_user_cache(user_id: str):
    """Invalidate all cache entries for a specific user"""
    invalidate_cache_pattern(f"cache:*:user:{user_id}*")
    invalidate_cache_pattern(f"cache:*:userId:{user_id}*")


def invalidate_project_cache(project_id: str):
    """Invalidate all cache entries for a specific project"""
    invalidate_cache_pattern(f"cache:*:project:{project_id}*")
    invalidate_cache_pattern(f"cache:*:projectId:{project_id}*")

