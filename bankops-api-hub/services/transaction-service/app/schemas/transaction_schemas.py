from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from shared.models.base import BaseModel


class CreateTransactionRequest(BaseModel):
    tenant_id: str
    transaction_type: Literal["transfer", "payment", "withdrawal", "deposit"]
    amount: Decimal = Field(gt=0, decimal_places=2)
    currency: str = Field(default="NGN", min_length=3, max_length=3)
    sender_account: str = Field(min_length=10, max_length=64)
    sender_bank_code: str | None = Field(default=None, max_length=16)
    receiver_account: str = Field(min_length=10, max_length=64)
    receiver_bank_code: str | None = Field(default=None, max_length=16)
    description: str | None = Field(default=None, max_length=256)
    channel: str = "api"
    reference: str | None = None
    correlation_id: str | None = None

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, v: str) -> str:
        return v.upper()


class TransactionResponse(BaseModel):
    id: str
    reference: str
    correlation_id: str
    tenant_id: str
    transaction_type: str
    status: str
    amount: Decimal
    currency: str
    sender_account: str
    receiver_account: str
    description: str | None
    channel: str
    created_at: str
    updated_at: str


class TransactionStatusUpdateRequest(BaseModel):
    status: str
    failure_reason: str | None = None
    external_ref: str | None = None
