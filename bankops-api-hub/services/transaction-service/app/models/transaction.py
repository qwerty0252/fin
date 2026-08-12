import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TransactionStatus(StrEnum):
    INITIATED = "initiated"
    VALIDATING = "validating"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"
    EXPIRED = "expired"


class TransactionType(StrEnum):
    TRANSFER = "transfer"
    PAYMENT = "payment"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    REVERSAL = "reversal"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    reference: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    correlation_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    transaction_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=TransactionStatus.INITIATED
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="NGN")

    sender_account: Mapped[str] = mapped_column(String(64), nullable=False)
    sender_bank_code: Mapped[str] = mapped_column(String(16), nullable=True)
    receiver_account: Mapped[str] = mapped_column(String(64), nullable=False)
    receiver_bank_code: Mapped[str] = mapped_column(String(16), nullable=True)

    description: Mapped[str] = mapped_column(String(256), nullable=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=True)  # api, mobile, ussd

    retry_count: Mapped[int] = mapped_column(default=0)
    failure_reason: Mapped[str] = mapped_column(String(512), nullable=True)
    external_ref: Mapped[str] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_transactions_status_tenant", "status", "tenant_id"),
        Index("ix_transactions_created_at", "created_at"),
    )
