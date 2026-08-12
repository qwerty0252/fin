"""Database models for the monitoring dashboard"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

Base = declarative_base()


class TransactionStateEnum(str, enum.Enum):
    """Transaction lifecycle states"""

    INITIATED = "INITIATED"
    AUTHORIZED = "AUTHORIZED"
    PROCESSING = "PROCESSING"
    SWITCHED = "SWITCHED"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"
    REFUNDED = "REFUNDED"
    TIMEOUT = "TIMEOUT"


class AlertSeverityEnum(str, enum.Enum):
    """Alert severity levels"""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Transaction(Base):
    """Transaction model"""

    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, unique=True, nullable=False, index=True)
    current_state = Column(String(50), nullable=False, default=TransactionStateEnum.INITIATED.value)
    amount = Column(Float, nullable=False)
    provider = Column(String, nullable=False)
    merchant = Column(String)
    reference = Column(String, unique=True, nullable=False, index=True)
    extra_data = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    # Relationships
    events = relationship("TransactionEvent", back_populates="transaction", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_created_at", "created_at"), Index("idx_current_state", "current_state"))


class TransactionEvent(Base):
    """Transaction event model for audit trail"""

    __tablename__ = "transaction_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True)
    previous_state = Column(String(50), nullable=True)
    new_state = Column(String(50), nullable=True)
    payload = Column(JSON, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    transaction = relationship("Transaction", back_populates="events")

    __table_args__ = (Index("idx_event_type", "event_type"), Index("idx_timestamp", "timestamp"))


class Alert(Base):
    """Alert model"""

    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    severity = Column(String(50), nullable=False)
    alert_type = Column(String, nullable=False, index=True)
    message = Column(String, nullable=False)
    status = Column(String, nullable=False, default="ACTIVE", index=True)
    extra_data = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)

    __table_args__ = (Index("idx_alert_type", "alert_type"), Index("idx_status", "status"))


class ServiceHealth(Base):
    """Service health status"""

    __tablename__ = "services"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    service_name = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False, default="UNKNOWN")
    last_heartbeat = Column(DateTime, nullable=False, default=datetime.utcnow)
    details = Column(JSON, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Metric(Base):
    """Metrics snapshot for caching"""

    __tablename__ = "metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String, nullable=False, index=True)
    metric_type = Column(String, nullable=False)  # counter, gauge, histogram
    value = Column(Float, nullable=False)
    labels = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (Index("idx_metric_name", "metric_name"), Index("idx_timestamp", "timestamp"))
