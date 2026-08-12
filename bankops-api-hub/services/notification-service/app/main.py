from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.routers import health, notifications

settings = get_settings()

app = FastAPI(
    title="BankOps Notification Service",
    description="Multi-channel alerting — Slack, email and webhook delivery",
    version="0.1.0",
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(health.router, tags=["Health"])
app.include_router(notifications.router, prefix="/api/v1", tags=["Notifications"])
