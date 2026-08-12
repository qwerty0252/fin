import time

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import get_settings

settings = get_settings()

_PUBLIC_PATHS = {"/health", "/metrics"}


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter backed by Redis."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        redis = getattr(request.app.state, "redis", None)
        if redis is None:
            return await call_next(request)

        identifier = (
            getattr(getattr(request.state, "user", None), "sub", None)
            or request.headers.get(settings.api_key_header)
            or request.client.host
        )

        window = 60  # seconds
        now = time.time()
        key = f"rl:{identifier}:{int(now // window)}"

        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, window * 2)

        limit = settings.rate_limit_requests_per_minute
        remaining = max(0, limit - count)

        if count > limit:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Retry after the current window."},
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(window),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
