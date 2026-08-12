"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List


class TransactionStateEnum(str, Enum):
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


class AlertSeverityEnum(str, Enum):
    """Alert severity levels"""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# Event Schemas
class TransactionEventInput(BaseModel):
    """Incoming transaction event"""

    transaction_id: str
    event_type: str
    amount: float
    provider: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class TransactionEventResponse(BaseModel):
    """Transaction event response"""

    id: str
    transaction_id: str
    event_type: str
    previous_state: Optional[TransactionStateEnum]
    new_state: Optional[TransactionStateEnum]
    payload: Optional[Dict[str, Any]]
    processing_time_ms: Optional[int]
    timestamp: datetime

    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionResponse(BaseModel):
    """Transaction response"""

    id: str
    transaction_id: str
    reference: str
    current_state: TransactionStateEnum
    amount: float
    provider: str
    merchant: Optional[str]
    metadata: Optional[Dict[str, Any]] = Field(None, validation_alias='extra_data')
    created_at: datetime
    updated_at: datetime
    events: List[TransactionEventResponse] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TransactionTraceResponse(BaseModel):
    """Transaction trace with timeline"""

    id: str
    transaction_id: str
    reference: str
    current_state: TransactionStateEnum
    amount: float
    provider: str
    timeline: List[TransactionEventResponse]
    total_processing_time_ms: int
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Alert Schemas
class AlertResponse(BaseModel):
    """Alert response"""

    id: str
    severity: AlertSeverityEnum
    alert_type: str
    message: str
    status: str
    metadata: Optional[Dict[str, Any]] = Field(None, validation_alias='extra_data')
    created_at: datetime
    resolved_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# Metrics Schemas
class MetricSnapshot(BaseModel):
    """Metrics snapshot"""

    tps: float  # Transactions per second
    rpm: float  # Transactions per minute
    success_rate: float
    failure_rate: float
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    active_transactions: int
    queue_depth: int
    retry_queue_depth: int
    connected_clients: int


class HealthStatus(BaseModel):
    """Service health status"""

    service_name: str
    status: str  # "HEALTHY", "DEGRADED", "DOWN"
    last_heartbeat: datetime
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class DashboardMetrics(BaseModel):
    """Complete dashboard metrics"""

    timestamp: datetime
    metrics: MetricSnapshot
    health: Dict[str, HealthStatus]
    active_alerts: List[AlertResponse]
    total_transactions: int
    transactions_by_state: Dict[str, int]
