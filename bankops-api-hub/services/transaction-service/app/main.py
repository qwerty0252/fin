from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.db.database import engine
from app.models.transaction import Base
from app.routers import health, transactions

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="BankOps Transaction Service",
    description="Transaction lifecycle management — creation, status tracking and event emission",
    version="0.1.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(health.router, tags=["Health"])
app.include_router(transactions.router, prefix="/api/v1", tags=["Transactions"])
