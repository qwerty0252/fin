import uuid
from datetime import datetime, timezone
from decimal import Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.models.transaction import Transaction, TransactionStatus
from shared.schemas.events import EventEnvelope, EventType
from shared.utils.logging import get_logger

logger = get_logger(__name__)


class TransactionService:
    def __init__(self, db: AsyncSession, settings: Settings) -> None:
        self._db = db
        self._settings = settings

    async def create_transaction(self, payload: dict) -> Transaction:
        reference = payload.get("reference") or f"TXN-{uuid.uuid4().hex[:12].upper()}"
        txn = Transaction(
            id=str(uuid.uuid4()),
            reference=reference,
            correlation_id=payload.get("correlation_id", str(uuid.uuid4())),
            tenant_id=payload["tenant_id"],
            transaction_type=payload["transaction_type"],
            amount=Decimal(str(payload["amount"])),
            currency=payload.get("currency", "NGN"),
            sender_account=payload["sender_account"],
            sender_bank_code=payload.get("sender_bank_code"),
            receiver_account=payload["receiver_account"],
            receiver_bank_code=payload.get("receiver_bank_code"),
            description=payload.get("description"),
            channel=payload.get("channel", "api"),
        )
        self._db.add(txn)
        await self._db.flush()
        await self._publish_event(txn, EventType.TRANSACTION_INITIATED)
        logger.info("transaction.created", txn_id=txn.id, reference=txn.reference)
        return txn

    async def get_transaction(self, txn_id: str) -> Transaction | None:
        result = await self._db.execute(select(Transaction).where(Transaction.id == txn_id))
        return result.scalar_one_or_none()

    async def get_by_reference(self, reference: str) -> Transaction | None:
        result = await self._db.execute(
            select(Transaction).where(Transaction.reference == reference)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        txn: Transaction,
        new_status: TransactionStatus,
        failure_reason: str | None = None,
        external_ref: str | None = None,
    ) -> Transaction:
        txn.status = new_status
        txn.updated_at = datetime.now(timezone.utc)
        if failure_reason:
            txn.failure_reason = failure_reason
        if external_ref:
            txn.external_ref = external_ref
        if new_status == TransactionStatus.COMPLETED:
            txn.completed_at = datetime.now(timezone.utc)
        await self._db.flush()
        logger.info("transaction.status_updated", txn_id=txn.id, status=new_status)
        return txn

    async def _publish_event(self, txn: Transaction, event_type: EventType) -> None:
        event = EventEnvelope(
            event_type=event_type,
            source_service=self._settings.service_name,
            correlation_id=txn.correlation_id,
            payload={
                "transaction_id": txn.id,
                "reference": txn.reference,
                "tenant_id": txn.tenant_id,
                "amount": str(txn.amount),
                "currency": txn.currency,
                "transaction_type": txn.transaction_type,
                "status": txn.status,
            },
        )
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{self._settings.event_bus_url}/api/v1/events/publish",
                    json=event.model_dump(mode="json"),
                )
        except Exception as exc:
            logger.warning("event.publish_failed", event_type=event_type, error=str(exc))
