from django.db import transaction
from .models import Message


STATUS_ORDER = {
    Message.STATUS_SENT: 0,
    Message.STATUS_DELIVERED: 1,
    Message.STATUS_READ: 2,
}


def advance_message_status(message, new_status: str) -> bool:
    
    current_order = STATUS_ORDER[message.status]
    new_order = STATUS_ORDER[new_status]

    if new_order <= current_order:
        return False

    message.status = new_status
    message.save(update_fields=["status", "updated_at"])
    return True
