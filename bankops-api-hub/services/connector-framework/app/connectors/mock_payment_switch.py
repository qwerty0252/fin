import random
import uuid
from decimal import Decimal

from app.base.connector import BaseConnector, ConnectorRequest, ConnectorResponse, ConnectorStatus
from app.config import get_settings
from shared.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class MockPaymentSwitch(BaseConnector):
    """
    Simulated payment switch for Phase 1 development.

    Behaviour:
    - Succeeds on most requests
    - Randomly fails based on MOCK_SWITCH_FAILURE_RATE
    - Returns realistic response shapes for integration testing
    """

    name = "mock_payment_switch"

    async def submit(self, request: ConnectorRequest) -> ConnectorResponse:
        failure_rate = settings.mock_switch_failure_rate

        logger.info(
            "mock_switch.submit",
            transaction_id=request.transaction_id,
            amount=request.amount,
        )

        if random.random() < failure_rate:
            return ConnectorResponse(
                connector_name=self.name,
                status=ConnectorStatus.FAILED,
                message="Simulated switch rejection: insufficient funds",
                raw_response={"error_code": "INSUFFICIENT_FUNDS"},
            )

        external_ref = f"MOCK-{uuid.uuid4().hex[:10].upper()}"
        return ConnectorResponse(
            connector_name=self.name,
            status=ConnectorStatus.SUCCESS,
            external_reference=external_ref,
            message="Transaction accepted by mock switch",
            raw_response={
                "switch_ref": external_ref,
                "amount": request.amount,
                "currency": request.currency,
                "sender": request.sender_account,
                "receiver": request.receiver_account,
                "session_id": uuid.uuid4().hex,
            },
        )

    async def query_status(self, external_reference: str) -> ConnectorResponse:
        return ConnectorResponse(
            connector_name=self.name,
            status=ConnectorStatus.SUCCESS,
            external_reference=external_reference,
            message="Status: COMPLETED (mock)",
            raw_response={"status": "COMPLETED"},
        )

    async def health_check(self) -> bool:
        return True
