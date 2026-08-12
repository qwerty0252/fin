from app.base.connector import BaseConnector, ConnectorRequest, ConnectorResponse, ConnectorStatus
from shared.utils.logging import get_logger

logger = get_logger(__name__)


class InternalAPIConnector(BaseConnector):
    """
    Connector for internal bank services (ledger, account validation, etc.)
    Phase 1: returns mock responses. Replace with real HTTP calls in Phase 2.
    """

    name = "internal_api"

    async def submit(self, request: ConnectorRequest) -> ConnectorResponse:
        logger.info("internal_api.submit", transaction_id=request.transaction_id)
        return ConnectorResponse(
            connector_name=self.name,
            status=ConnectorStatus.SUCCESS,
            external_reference=f"INT-{request.transaction_id[:8].upper()}",
            message="Posted to internal ledger (mock)",
        )

    async def query_status(self, external_reference: str) -> ConnectorResponse:
        return ConnectorResponse(
            connector_name=self.name,
            status=ConnectorStatus.SUCCESS,
            external_reference=external_reference,
            message="Internal ledger confirms: POSTED",
        )

    async def health_check(self) -> bool:
        return True
