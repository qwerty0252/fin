from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.routers import health, workflows

settings = get_settings()

app = FastAPI(
    title="BankOps Orchestration Engine",
    description="Multi-step transaction workflow execution with retries, rollback and tracing",
    version="0.1.0",
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(health.router, tags=["Health"])
app.include_router(workflows.router, prefix="/api/v1", tags=["Workflows"])
