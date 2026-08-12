from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import TransactionCreate
from models.entities import RetryRecord, ReversalRecord, Transaction, TransactionEvent
from models.enums import EventType, TransactionStatus


class TransactionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transaction(self, data: TransactionCreate) -> Transaction:
        transaction = Transaction(
            reference=data.reference,
            account_number=data.account_number,
            amount=Decimal(data.amount),
            currency=data.currency,
            channel=data.channel,
            transaction_type=data.transaction_type,
            status=TransactionStatus.INITIATED,
            idempotency_key=data.idempotency_key,
        )
        self.session.add(transaction)
        await self.session.flush()
        await self.add_event(transaction.id, EventType.TRANSACTION_CREATED.value, {"reference": data.reference})
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_transaction(self, transaction_id: UUID) -> Transaction | None:
        result = await self.session.execute(select(Transaction).where(Transaction.id == transaction_id))
        return result.scalar_one_or_none()

    async def list_transactions(self, limit: int = 100, offset: int = 0) -> tuple[list[Transaction], int]:
        records_result = await self.session.execute(
            select(Transaction).order_by(Transaction.created_at.desc()).offset(offset).limit(limit)
        )
        count_result = await self.session.execute(select(func.count()).select_from(Transaction))
        return records_result.scalars().all(), int(count_result.scalar_one())

    async def update_status(self, transaction_id: UUID, status: TransactionStatus) -> None:
        transaction = await self.get_transaction(transaction_id)
        if not transaction:
            return
        transaction.status = status
        transaction.updated_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def add_event(self, transaction_id: UUID, event_type: str, payload: dict) -> None:
        self.session.add(
            TransactionEvent(transaction_id=transaction_id, event_type=event_type, payload=payload)
        )
        await self.session.flush()

    async def record_retry(self, transaction_id: UUID, retry_count: int, next_retry_at: datetime | None) -> None:
        self.session.add(
            RetryRecord(
                transaction_id=transaction_id,
                retry_count=retry_count,
                next_retry_at=next_retry_at,
            )
        )
        await self.session.flush()

    async def record_reversal(self, transaction_id: UUID, reason: str, status: str = "REQUESTED") -> None:
        self.session.add(ReversalRecord(transaction_id=transaction_id, reason=reason, status=status))
        await self.session.flush()
