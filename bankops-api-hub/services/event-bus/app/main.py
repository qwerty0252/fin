from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.broker.rabbitmq import RabbitMQBroker
from app.config import get_settings
from app.routers import events, health

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    broker = RabbitMQBroker(settings)
    await broker.connect()
    app.state.broker = broker
    yield
    await broker.close()


app = FastAPI(
    title="BankOps Event Bus",
    description="Async event publishing, queue management, retries and dead-letter handling",
    version="0.1.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(health.router, tags=["Health"])
app.include_router(events.router, prefix="/api/v1", tags=["Events"])
