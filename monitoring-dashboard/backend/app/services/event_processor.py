"""Event processing service"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.models import TransactionStateEnum
from app.services import StateTransitionValidator, StateTransitionError
from app.utils.db import TransactionRepository, EventRepository
from app.observability import log_event, events_processed_total
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EventProcessingService:
    """Service for processing transaction events"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.transaction_repo = TransactionRepository(db)
        self.event_repo = EventRepository(db)

    async def process_event(
        self,
        transaction_id: str,
        event_type: str,
        amount: float,
        provider: str,
        merchant: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """Process a transaction event and update state"""
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Get or create transaction
        transaction = await self.transaction_repo.get_transaction(transaction_id)
        is_new = transaction is None

        if not transaction:
            # Create new transaction — already set to INITIATED by default
            transaction = await self.transaction_repo.create_transaction(
                transaction_id=transaction_id,
                reference=f"REF_{transaction_id}",
                amount=amount,
                provider=provider,
                merchant=merchant,
                metadata=metadata,
            )
            log_event("transaction_created", {"transaction_id": transaction_id, "amount": amount})

        # Determine state transition
        new_state = self._map_event_to_state(event_type)
        previous_state = transaction.current_state

        # Skip transition check for new transactions already in the target state
        if is_new and new_state == TransactionStateEnum.INITIATED:
            # Transaction was just created in INITIATED state — nothing to transition
            pass
        elif not StateTransitionValidator.is_valid_transition(previous_state, new_state):
            logger.warning(
                f"Invalid state transition: {previous_state} -> {new_state} for transaction {transaction_id}"
            )
            raise StateTransitionError(f"Cannot transition from {previous_state} to {new_state}")
        else:
            # Update transaction state
            transaction = await self.transaction_repo.update_transaction_state(transaction_id, new_state)

        # Record event using the DB primary key (UUID), not the business transaction_id
        await self.event_repo.create_event(
            transaction_id=transaction.id,
            event_type=event_type,
            previous_state=previous_state,
            new_state=new_state,
            payload=metadata,
        )

        # Log event
        events_processed_total.labels(event_type=event_type).inc()
        log_event(
            "event_processed",
            {
                "transaction_id": transaction_id,
                "event_type": event_type,
                "previous_state": str(previous_state),
                "new_state": str(new_state),
            },
        )

        return True

    def _map_event_to_state(self, event_type: str) -> TransactionStateEnum:
        """Map event type to transaction state.
        Handles both plain ('INITIATED') and prefixed ('TRANSACTION_INITIATED') formats.
        """
        # Strip common prefixes (e.g. TRANSACTION_INITIATED -> INITIATED)
        normalized = event_type.upper()
        for prefix in ("TRANSACTION_", "TXN_"):
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
                break

        event_mapping = {
            "INITIATED": TransactionStateEnum.INITIATED,
            "AUTHORIZED": TransactionStateEnum.AUTHORIZED,
            "PROCESSING": TransactionStateEnum.PROCESSING,
            "SWITCHED": TransactionStateEnum.SWITCHED,
            "SETTLED": TransactionStateEnum.SETTLED,
            "FAILED": TransactionStateEnum.FAILED,
            "REVERSED": TransactionStateEnum.REVERSED,
            "REFUNDED": TransactionStateEnum.REFUNDED,
            "TIMEOUT": TransactionStateEnum.TIMEOUT,
        }
        return event_mapping.get(normalized, TransactionStateEnum.INITIATED)
