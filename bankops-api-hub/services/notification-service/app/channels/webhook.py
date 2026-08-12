from typing import Any

import httpx

from shared.utils.logging import get_logger

logger = get_logger(__name__)


class WebhookChannel:
    async def send(self, url: str, payload: dict[str, Any]) -> bool:
        if not url:
            return False
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload)
                logger.info(
                    "webhook.sent",
                    url=url,
                    status_code=response.status_code,
                )
                return response.status_code < 400
        except Exception as exc:
            logger.warning("webhook.failed", url=url, error=str(exc))
            return False
