from .models import Message, MessageDelivery, MessageRead
from apps.conversations.models import Conversation, ConversationMember


STATUS_ORDER = {
    Message.STATUS_SENT: 0,
    Message.STATUS_DELIVERED: 1,
    Message.STATUS_READ: 2,
}


def advance_message_status(message, new_status):
    current_order = STATUS_ORDER[message.status]
    new_order = STATUS_ORDER[new_status]

    if new_order <= current_order:
        return False

    message.status = new_status
    message.save(update_fields=["status", "updated_at"])
    return True


def initialize_group_recipients(message):
    if message.conversation.type != Conversation.TypeChoices.GROUP:
        return

    recipient_ids = ConversationMember.objects.filter(
        conversation_id=message.conversation_id,
        joined_at__lte=message.created_at,
    ).exclude(
        user_id=message.sender_id,
    ).values_list(
        "user_id",
        flat=True,
    )

    MessageDelivery.objects.bulk_create(
        [
            MessageDelivery(
                message=message,
                user_id=user_id,
            )
            for user_id in recipient_ids
        ],
        ignore_conflicts=True,
    )


def recalculate_group_message_status(message):
    if message.conversation.type != Conversation.TypeChoices.GROUP:
        return False

    initialize_group_recipients(message)

    recipient_ids = list(
        MessageDelivery.objects.filter(
            message=message,
        ).values_list(
            "user_id",
            flat=True,
        )
    )

    if not recipient_ids:
        return False

    read_count = MessageRead.objects.filter(
        message=message,
        user_id__in=recipient_ids,
    ).count()

    if read_count == len(recipient_ids):
        target_status = Message.STATUS_READ

    elif MessageDelivery.objects.filter(
        message=message,
        user_id__in=recipient_ids,
        delivered_at__isnull=True,
    ).exists():
        target_status = Message.STATUS_SENT

    else:
        target_status = Message.STATUS_DELIVERED

    return advance_message_status(message, target_status)
