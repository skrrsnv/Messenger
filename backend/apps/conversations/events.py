import json
import logging

import redis
from django.conf import settings

logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


def publish_message_created(event: dict) -> None:
    try:
        redis_client.publish(
            "chat.events",
            json.dumps(event),
        )
    except Exception:
        logger.exception(
            "Failed to publish message.created event"
        )