from rest_framework.permissions import BasePermission
from .models import Conversation, ConversationMember


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


class CanUpdateConversation(BasePermission):
    def has_permission(self, request, view):
        conversation_id = get_conversation_id(view)

        membership = (
            ConversationMember.objects
            .select_related("conversation")
            .filter(
                conversation_id=conversation_id,
                user=request.user,
            )
            .first()
        )

        if membership is None:
            return False

        if membership.conversation.type == Conversation.TypeChoices.PRIVATE:
            return False

        return membership.role in [
            ConversationMember.RoleChoices.ADMIN,
            ConversationMember.RoleChoices.OWNER,
        ]


class CanDeleteConversation(BasePermission):
    def has_permission(self, request, view):
        conversation_id = get_conversation_id(view)

        membership = (
            ConversationMember.objects
            .select_related("conversation")
            .filter(
                conversation_id=conversation_id,
                user=request.user,
            )
            .first()
        )

        if membership is None:
            return False

        if membership.conversation.type == Conversation.TypeChoices.PRIVATE:
            return True

        return membership.role == ConversationMember.RoleChoices.OWNER


class CanManageMembers(BasePermission):
    def has_permission(self, request, view):
        conversation_id = get_conversation_id(view)

        membership = (
            ConversationMember.objects
            .select_related("conversation")
            .filter(
                conversation_id=conversation_id,
                user=request.user,
            )
            .first()
        )

        if membership is None:
            return False

        if membership.conversation.type == Conversation.TypeChoices.PRIVATE:
            return False

        return membership.role in [
            ConversationMember.RoleChoices.ADMIN,
            ConversationMember.RoleChoices.OWNER,
        ]


class CanChangeMemberRole(BasePermission):
    def has_permission(self, request, view):
        conversation_id = get_conversation_id(view)

        membership = ConversationMember.objects.filter(
            conversation_id=conversation_id,
            user=request.user,
            role=ConversationMember.RoleChoices.OWNER,
        ).first()

        return membership is not None


class CanRemoveMember(BasePermission):
    def has_permission(self, request, view):
        conversation_id = get_conversation_id(view)

        membership = (
            ConversationMember.objects
            .select_related("conversation")
            .filter(
                conversation_id=conversation_id,
                user=request.user,
            )
            .first()
        )

        if membership is None:
            return False

        if membership.conversation.type == Conversation.TypeChoices.PRIVATE:
            return False

        return membership.role in [
            ConversationMember.RoleChoices.ADMIN,
            ConversationMember.RoleChoices.OWNER,
        ]

    def has_object_permission(self, request, view, obj):
        requester = obj.conversation.members.get(
            user=request.user
        )

        if requester.role == ConversationMember.RoleChoices.OWNER:
            return obj.role != ConversationMember.RoleChoices.OWNER

        if requester.role == ConversationMember.RoleChoices.ADMIN:
            return obj.role == ConversationMember.RoleChoices.MEMBER

        return False