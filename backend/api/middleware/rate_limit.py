"""Rate limiting middleware using Redis sliding window"""
import time
from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging
from api.lib.redis import get_redis_client
from api.middleware.auth import get_current_user

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Rate limit configuration for an endpoint"""

    def __init__(
        self,
        requests: int,
        window_seconds: int,
        key_func: Optional[Callable[[Request], str]] = None,
    ):
        """
        Args:
            requests: Number of requests allowed
            window_seconds: Time window in seconds
            key_func: Function to generate rate limit key from request
        """
        self.requests = requests
        self.window_seconds = window_seconds
        self.key_func = key_func or self._default_key_func

    def _default_key_func(self, request: Request) -> str:
        """Default key function: rate limit by IP address"""
        return f"rate_limit:ip:{request.client.host}"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis sliding window algorithm.
    """

    def __init__(
        self,
        app,
        default_limit: Optional[RateLimitConfig] = None,
        endpoint_limits: Optional[dict[str, RateLimitConfig]] = None,
    ):
        super().__init__(app)
        # Default: 100 requests per minute per IP
        self.default_limit = default_limit or RateLimitConfig(
            requests=100, window_seconds=60
        )
        # Endpoint-specific limits
        self.endpoint_limits = endpoint_limits or {}

    async def dispatch(self, request: Request, call_next: Callable):
        # Get rate limit config for this endpoint
        limit_config = self.endpoint_limits.get(
            request.url.path, self.default_limit
        )

        # Generate rate limit key
        rate_limit_key = limit_config.key_func(request)

        # Check rate limit
        redis_client = get_redis_client()
        if redis_client:
            try:
                if not self._check_rate_limit(
                    redis_client, rate_limit_key, limit_config
                ):
                    # Rate limit exceeded
                    retry_after = self._get_retry_after(
                        redis_client, rate_limit_key, limit_config
                    )
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Please try again later.",
                        headers={"Retry-After": str(retry_after)},
                    )
            except HTTPException:
                raise
            except Exception as e:
                logger.warning(f"Rate limit check error: {e}. Allowing request.")
                # On error, allow request (fail open)

        return await call_next(request)

    def _check_rate_limit(
        self, redis_client, key: str, config: RateLimitConfig
    ) -> bool:
        """
        Check if request is within rate limit using sliding window.
        Returns True if allowed, False if rate limit exceeded.
        """
        now = time.time()
        window_start = now - config.window_seconds

        # Use sorted set to track requests in time window
        # Score is timestamp, value is request ID (unique per request)
        pipe = redis_client.pipeline()

        # Remove old entries outside window
        pipe.zremrangebyscore(key, 0, window_start)

        # Count current requests in window
        pipe.zcard(key)

        # Add current request
        request_id = f"{now}:{time.time_ns()}"
        pipe.zadd(key, {request_id: now})

        # Set expiration
        pipe.expire(key, config.window_seconds + 1)

        results = pipe.execute()
        current_count = results[1]

        return current_count < config.requests

    def _get_retry_after(
        self, redis_client, key: str, config: RateLimitConfig
    ) -> int:
        """Get seconds until rate limit window resets"""
        now = time.time()
        window_start = now - config.window_seconds

        # Get oldest request timestamp
        oldest = redis_client.zrange(key, 0, 0, withscores=True)
        if oldest:
            oldest_time = oldest[0][1]
            retry_after = int(config.window_seconds - (now - oldest_time)) + 1
            return max(1, retry_after)

        return config.window_seconds


def user_rate_limit_key(request: Request) -> str:
    """Generate rate limit key from authenticated user"""
    try:
        # Try to get user from request state (set by auth middleware)
        if hasattr(request.state, "user_id"):
            return f"rate_limit:user:{request.state.user_id}"
    except Exception:
        pass

    # Fallback to IP
    return f"rate_limit:ip:{request.client.host}"


# Predefined rate limit configs
RATE_LIMIT_STRICT = RateLimitConfig(requests=10, window_seconds=60, key_func=user_rate_limit_key)
RATE_LIMIT_MODERATE = RateLimitConfig(requests=50, window_seconds=60, key_func=user_rate_limit_key)
RATE_LIMIT_LOOSE = RateLimitConfig(requests=200, window_seconds=60, key_func=user_rate_limit_key)

# Endpoint-specific rate limits
DEFAULT_ENDPOINT_LIMITS = {
    "/api/projects": RateLimitConfig(
        requests=100, window_seconds=60, key_func=user_rate_limit_key
    ),
    # AI endpoints will have stricter limits
    # "/api/agents/*/chat": RATE_LIMIT_STRICT,
    # "/api/agents/*/execute": RATE_LIMIT_STRICT,
}

