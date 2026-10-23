import logging

from apps.conversations.events import redis_client

logger = logging.getLogger(__name__)


def publish_message_event(event: dict) -> None:
    event_type = event.get("type", "unknown")

    try:
        redis_client.publish(
            "chat.events",
            json_dumps(event),
        )
    except Exception:
        logger.exception(
            "Failed to publish %s event",
            event_type,
        )


def json_dumps(event: dict) -> str:
    import json
    return json.dumps(event)
