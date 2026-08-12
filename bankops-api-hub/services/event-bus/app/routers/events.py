from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.config import get_settings
from shared.schemas.events import EventEnvelope
from shared.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()

_QUEUE_ROUTING: dict[str, str] = {
    "transaction": settings.transaction_queue,
    "orchestration": settings.orchestration_queue,
    "notification": settings.notification_queue,
}


@router.post("/events/publish", status_code=status.HTTP_202_ACCEPTED)
async def publish_event(event: EventEnvelope, request: Request) -> JSONResponse:
    broker = request.app.state.broker
    # Derive routing key from event type prefix (e.g. "transaction.initiated" → transaction queue)
    prefix = event.event_type.split(".")[0]
    routing_key = _QUEUE_ROUTING.get(prefix, settings.transaction_queue)

    await broker.publish(event, routing_key=routing_key)
    logger.info("event.accepted", event_id=event.event_id, event_type=event.event_type)

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"event_id": event.event_id, "status": "accepted"},
    )
