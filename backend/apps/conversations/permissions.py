from rest_framework.permissions import BasePermission
from .models import ConversationMember


def get_conversation_id(view):
    return (
        view.kwargs.get("conversation_id")
        or view.kwargs.get("pk")
    )


class IsConversationMember(BasePermission):
    def has_permission(self, request, view):
        conversation_id = get_conversation_id(view)

        if conversation_id is None:
            return False

        return ConversationMember.objects.filter(
            conversation_id=conversation_id,
            user=request.user,
        ).exists()


class IsConversationAdmin(BasePermission):
    def has_permission(self, request, view):
        conversation_id = get_conversation_id(view)

        if conversation_id is None:
            return False

        return ConversationMember.objects.filter(
            conversation_id=conversation_id,
            user=request.user,
            role__in=[
                ConversationMember.RoleChoices.ADMIN,
                ConversationMember.RoleChoices.OWNER,
            ],
        ).exists()


class IsConversationOwner(BasePermission):
    def has_permission(self, request, view):
        conversation_id = get_conversation_id(view)

        if conversation_id is None:
            return False

        return ConversationMember.objects.filter(
            conversation_id=conversation_id,
            user=request.user,
            role=ConversationMember.RoleChoices.OWNER,
        ).exists()