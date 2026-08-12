import httpx

from app.config import Settings
from shared.utils.logging import get_logger

logger = get_logger(__name__)


class SlackChannel:
    def __init__(self, settings: Settings) -> None:
        self._webhook_url = settings.slack_webhook_url

    async def send(self, message: str, context: dict) -> bool:
        if not self._webhook_url:
            logger.debug("slack.skipped", reason="no webhook configured")
            return False
        payload = {
            "text": message,
            "attachments": [
                {
                    "color": "#36a64f" if context.get("status") == "completed" else "#ff0000",
                    "fields": [
                        {"title": k, "value": str(v), "short": True}
                        for k, v in context.items()
                    ],
                }
            ],
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self._webhook_url, json=payload)
                return response.status_code == 200
        except Exception as exc:
            logger.warning("slack.send_failed", error=str(exc))
            return False
