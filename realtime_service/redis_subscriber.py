import asyncio
import json
import logging
import os

import redis.asyncio as redis

from .connection_manager import ConnectionManager

logger = logging.getLogger(__name__)

REDIS_URL = os.environ["REDIS_URL"]
CHANNEL = "chat.events"


async def redis_event_listener(
    manager: ConnectionManager,
    client: redis.Redis,
):
    while True:
        pubsub = client.pubsub()

        try:
            await pubsub.subscribe(CHANNEL)
            logger.info("Subscribed to Redis channel %s", CHANNEL)

            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue

                try:
                    event = json.loads(message["data"])

                    if event.get("type") not in (
                        "message.created",
                        "typing.start",
                        "typing.stop",
                        "presence.update",
                    ):
                        continue

                    conversation_id = int(
                        event["conversation_id"]
                    )

                    await manager.broadcast_json(
                        conversation_id,
                        event,
                    )

                except (ValueError, TypeError, KeyError):
                    logger.exception(
                        "Invalid event received from Redis"
                    )

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception(
                "Redis subscriber failed; reconnecting"
            )
            await asyncio.sleep(2)

        finally:
            await pubsub.aclose()