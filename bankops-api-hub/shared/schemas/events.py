import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import Field

from shared.models.base import BaseModel


class EventType(StrEnum):
    # Transaction lifecycle
    TRANSACTION_INITIATED = "transaction.initiated"
    TRANSACTION_VALIDATED = "transaction.validated"
    TRANSACTION_ROUTED = "transaction.routed"
    TRANSACTION_SUBMITTED = "transaction.submitted"
    TRANSACTION_COMPLETED = "transaction.completed"
    TRANSACTION_FAILED = "transaction.failed"
    TRANSACTION_REVERSED = "transaction.reversed"

    # Fraud
    FRAUD_CHECK_PASSED = "fraud.check.passed"
    FRAUD_CHECK_FAILED = "fraud.check.failed"

    # Settlement
    SETTLEMENT_INITIATED = "settlement.initiated"
    SETTLEMENT_CONFIRMED = "settlement.confirmed"
    SETTLEMENT_FAILED = "settlement.failed"

    # Connector
    CONNECTOR_REQUEST_SENT = "connector.request.sent"
    CONNECTOR_RESPONSE_RECEIVED = "connector.response.received"
    CONNECTOR_ERROR = "connector.error"

    # Notification
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_FAILED = "notification.failed"

    # System
    DEAD_LETTER = "system.dead_letter"


class EventEnvelope(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    source_service: str
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0"
    payload: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    retry_count: int = 0

    def to_message_body(self) -> bytes:
        return self.model_dump_json().encode("utf-8")

    @classmethod
    def from_message_body(cls, body: bytes) -> "EventEnvelope":
        return cls.model_validate_json(body)
