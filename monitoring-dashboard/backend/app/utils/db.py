"""Database utilities"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import Transaction, TransactionEvent, TransactionStateEnum
from typing import Optional, List
from datetime import datetime


class TransactionRepository:
    """Repository for transaction data access"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_transaction(
        self,
        transaction_id: str,
        reference: str,
        amount: float,
        provider: str,
        merchant: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Transaction:
        """Create a new transaction"""
        transaction = Transaction(
            transaction_id=transaction_id,
            reference=reference,
            amount=amount,
            provider=provider,
            merchant=merchant,
            extra_data=metadata,
            current_state=TransactionStateEnum.INITIATED,
        )
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID with events eagerly loaded"""
        result = await self.db.execute(
            select(Transaction)
            .options(selectinload(Transaction.events))
            .where(Transaction.transaction_id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def update_transaction_state(
        self, transaction_id: str, new_state: TransactionStateEnum
    ) -> Optional[Transaction]:
        """Update transaction state"""
        transaction = await self.get_transaction(transaction_id)
        if transaction:
            transaction.current_state = new_state
            transaction.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(transaction)
        return transaction

    async def list_transactions(self, limit: int = 100, offset: int = 0) -> List[Transaction]:
        """List transactions with pagination"""
        result = await self.db.execute(
            select(Transaction)
            .options(selectinload(Transaction.events))
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def count_transactions(self) -> int:
        """Count total transactions"""
        result = await self.db.execute(select(Transaction).with_only_columns(1))
        return result.scalar()


class EventRepository:
    """Repository for transaction event data access"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_event(
        self,
        transaction_id: str,
        event_type: str,
        previous_state: Optional[TransactionStateEnum] = None,
        new_state: Optional[TransactionStateEnum] = None,
        payload: Optional[dict] = None,
        processing_time_ms: Optional[int] = None,
    ) -> TransactionEvent:
        """Create a new transaction event"""
        event = TransactionEvent(
            transaction_id=transaction_id,
            event_type=event_type,
            previous_state=previous_state,
            new_state=new_state,
            payload=payload,
            processing_time_ms=processing_time_ms,
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def get_transaction_events(self, transaction_id: str) -> List[TransactionEvent]:
        """Get all events for a transaction"""
        result = await self.db.execute(
            select(TransactionEvent)
            .where(TransactionEvent.transaction_id == transaction_id)
            .order_by(TransactionEvent.timestamp.asc())
        )
        return result.scalars().all()
