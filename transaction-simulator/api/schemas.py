from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from models.enums import TransactionStatus


class SimulationRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=10000)
    duplicates: bool = False


class TransactionCreate(BaseModel):
    reference: str
    account_number: str
    amount: Decimal
    currency: str
    channel: str
    transaction_type: str
    idempotency_key: str | None = None


class TransactionResponse(BaseModel):
    id: UUID
    reference: str
    account_number: str
    amount: Decimal
    currency: str
    channel: str
    transaction_type: str
    status: TransactionStatus
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int


class RetryRequest(BaseModel):
    reason: str = "manual_retry"
    reset_retry_count: bool = True
    immediate: bool = True
    force: bool = False


class ReverseRequest(BaseModel):
    reason: str = "manual_reversal"
