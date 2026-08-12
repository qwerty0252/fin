from typing import Any, Literal

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl

from app.channels.slack import SlackChannel
from app.channels.webhook import WebhookChannel
from app.config import Settings, get_settings

router = APIRouter()


class NotifyRequest(BaseModel):
    transaction_id: str
    correlation_id: str
    tenant_id: str
    status: Literal["completed", "failed", "pending"]
    channel: Literal["slack", "webhook", "all"] = "all"
    webhook_url: str | None = None
    message: str | None = None


@router.post("/notify", status_code=status.HTTP_202_ACCEPTED)
async def send_notification(
    body: NotifyRequest,
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    context: dict[str, Any] = {
        "transaction_id": body.transaction_id,
        "correlation_id": body.correlation_id,
        "tenant_id": body.tenant_id,
        "status": body.status,
    }
    message = body.message or (
        f"Transaction {body.transaction_id} {body.status.upper()}"
    )
    results: dict[str, bool] = {}

    if body.channel in ("slack", "all"):
        slack = SlackChannel(settings)
        results["slack"] = await slack.send(message, context)

    if body.channel in ("webhook", "all") and body.webhook_url:
        webhook = WebhookChannel()
        results["webhook"] = await webhook.send(body.webhook_url, context)

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"queued": True, "channels": results},
    )
