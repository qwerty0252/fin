from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.routers import connectors, health

settings = get_settings()

app = FastAPI(
    title="BankOps Connector Framework",
    description="Pluggable financial system connectors — mock switch, internal APIs, payment providers",
    version="0.1.0",
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(health.router, tags=["Health"])
app.include_router(connectors.router, prefix="/api/v1", tags=["Connectors"])
