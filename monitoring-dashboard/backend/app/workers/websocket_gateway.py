"""WebSocket gateway for real-time dashboard updates"""

import asyncio
import json
import logging
from fastapi import FastAPI, WebSocket
from app.config import get_settings
from app.utils.redis import redis_client
from app.observability import connected_clients

logger = logging.getLogger(__name__)
settings = get_settings()

# WebSocket app
ws_app = FastAPI(title="WebSocket Gateway")

# Connected clients
clients = set()


@ws_app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for dashboard updates"""
    await websocket.accept()
    clients.add(websocket)
    connected_clients.set(len(clients))
    logger.info(f"Client connected. Total clients: {len(clients)}")

    try:
        while True:
            # Keep connection alive and receive messages
            data = await websocket.receive_text()
            # Process incoming commands if any
            logger.debug(f"Received: {data}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        clients.remove(websocket)
        connected_clients.set(len(clients))
        logger.info(f"Client disconnected. Total clients: {len(clients)}")


async def broadcast_update(message: dict):
    """Broadcast update to all connected clients"""
    disconnected = set()
    for client in clients:
        try:
            await client.send_json(message)
        except Exception as e:
            logger.error(f"Error sending to client: {str(e)}")
            disconnected.add(client)

    # Clean up disconnected clients
    for client in disconnected:
        clients.discard(client)
        connected_clients.set(len(clients))


async def listen_redis():
    """Listen for Redis pub/sub messages and broadcast"""
    pubsub = redis_client.client.pubsub()
    await pubsub.subscribe("transaction_updates", "alert_triggered", "service_down")

    logger.info("Started listening to Redis pub/sub")

    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            logger.debug(f"Broadcasting: {data}")
            await broadcast_update(data)


async def main():
    """Start WebSocket gateway"""
    logger.info("Starting WebSocket Gateway")

    await redis_client.connect()

    # Start listening to Redis
    await listen_redis()


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level)
    asyncio.run(main())
