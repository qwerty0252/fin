from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class ConnectorStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    TIMEOUT = "timeout"
    REJECTED = "rejected"


class ConnectorRequest(BaseModel):
    transaction_id: str
    correlation_id: str
    amount: str
    currency: str = "NGN"
    sender_account: str
    receiver_account: str
    sender_bank_code: str | None = None
    receiver_bank_code: str | None = None
    description: str | None = None
    metadata: dict[str, Any] = {}


class ConnectorResponse(BaseModel):
    connector_name: str
    status: ConnectorStatus
    external_reference: str | None = None
    message: str | None = None
    raw_response: dict[str, Any] = {}


class BaseConnector(ABC):
    name: str = "base"

    @abstractmethod
    async def submit(self, request: ConnectorRequest) -> ConnectorResponse: ...

    @abstractmethod
    async def query_status(self, external_reference: str) -> ConnectorResponse: ...

    @abstractmethod
    async def health_check(self) -> bool: ...
