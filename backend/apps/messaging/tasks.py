import logging
import redis
from celery import shared_task
from django.conf import settings
from apps.conversations.models import ConversationMember
from .models import Message, Notification


logger = logging.getLogger(__name__)


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def create_offline_notifications(message_id: int):

    message = Message.objects.select_related(
        "conversation",
        "sender",
    ).get(pk=message_id)

    recipients = ConversationMember.objects.filter(
        conversation_id=message.conversation_id,
    ).exclude(
        user_id=message.sender_id,
    ).values_list(
        "user_id",
        flat=True,
    )

    redis_client = redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )

    try:
        offline_user_ids = []

        for user_id in recipients:
            presence_key = (
                f"presence:user:{user_id}:connections"
            )

            if not redis_client.exists(presence_key):
                offline_user_ids.append(user_id)

        notifications = [
            Notification(
                user_id=user_id,
                message=message,
            )
            for user_id in offline_user_ids
        ]

        if notifications:
            Notification.objects.bulk_create(
                notifications,
                ignore_conflicts=True,
            )

        logger.info(
            "Created %s offline notifications for message %s",
            len(notifications),
            message_id,
        )

    finally:
        redis_client.close()