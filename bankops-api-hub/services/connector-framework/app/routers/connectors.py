from fastapi import APIRouter, HTTPException, Path, status

from app.base.connector import ConnectorRequest, ConnectorResponse
from app.connectors.internal_api import InternalAPIConnector
from app.connectors.mock_payment_switch import MockPaymentSwitch

router = APIRouter()

_REGISTRY: dict = {
    "mock_payment_switch": MockPaymentSwitch(),
    "internal_api": InternalAPIConnector(),
}


def _get_connector(connector_name: str):
    connector = _REGISTRY.get(connector_name)
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connector '{connector_name}' not found",
        )
    return connector


@router.get("/connectors")
async def list_connectors() -> dict:
    return {
        "connectors": [
            {"name": name, "type": type(c).__name__} for name, c in _REGISTRY.items()
        ]
    }


@router.post(
    "/connectors/{connector_name}/submit",
    response_model=ConnectorResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_to_connector(
    connector_name: str = Path(...),
    body: ConnectorRequest = ...,
) -> ConnectorResponse:
    connector = _get_connector(connector_name)
    return await connector.submit(body)


@router.get(
    "/connectors/{connector_name}/status/{external_ref}",
    response_model=ConnectorResponse,
)
async def query_connector_status(
    connector_name: str = Path(...),
    external_ref: str = Path(...),
) -> ConnectorResponse:
    connector = _get_connector(connector_name)
    return await connector.query_status(external_ref)


@router.get("/connectors/{connector_name}/health")
async def connector_health(connector_name: str = Path(...)) -> dict:
    connector = _get_connector(connector_name)
    healthy = await connector.health_check()
    return {"connector": connector_name, "healthy": healthy}
