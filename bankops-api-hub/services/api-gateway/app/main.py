from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.request_logger import RequestLoggerMiddleware
from app.routers import auth, health, proxy

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    app.state.redis = await aioredis.from_url(
        settings.redis_url, encoding="utf-8", decode_responses=True
    )
    yield
    # Shutdown
    await app.state.redis.aclose()


app = FastAPI(
    title="BankOps API Gateway",
    description="Authentication, routing, rate limiting and request logging for BankOps services",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ─── Middleware (applied in reverse order) ────────────────────────────────────
app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app_env == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Prometheus metrics ───────────────────────────────────────────────────────
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(proxy.router, prefix="/api/v1", tags=["Proxy"])
