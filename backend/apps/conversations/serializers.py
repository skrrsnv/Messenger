from rest_framework import serializers
from django.db import transaction
from .models import Conversation, ConversationMember
from django.contrib.auth import get_user_model

User = get_user_model()

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            'id',
            'type',
            'title',
            'avatar',
            'created_at',
            'updated_at',    
        ]
        

class ConversationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMember
        fields = [
            'id',
            'conversation',
            'user',
            'role',
            'joined_at',
        ]
        

class PrivateConversationCreateSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        error_messages={"does_not_exist": "User does not exist."}
    )

    def validate_user_id(self, user):
        request = self.context["request"]

        if user == request.user:
            raise serializers.ValidationError(
                "You cannot create a conversation with yourself."
            )

        return user
    
    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        user = validated_data["user_id"]

        conversation = (
            Conversation.objects
            .filter(
                type=Conversation.TypeChoices.PRIVATE,
                members__user=request.user,
            )
            .filter(members__user=user)
            .distinct()
            .first()
        )

        if conversation:
            return conversation

        conversation = Conversation.objects.create(
            type=Conversation.TypeChoices.PRIVATE,
        )

        ConversationMember.objects.create(
            conversation=conversation,
            user=request.user,
            role=ConversationMember.RoleChoices.OWNER,
        )

        ConversationMember.objects.create(
            conversation=conversation,
            user=user,
            role=ConversationMember.RoleChoices.MEMBER,
        )

        return conversation


class GroupConversationCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    user_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
    )

    def validate_user_ids(self, users):
        request = self.context["request"]

        if request.user in users:
            raise serializers.ValidationError(
                "You cannot add yourself to user_ids."
            )

        if not users:
            raise serializers.ValidationError(
                "At least one user is required."
            )

        return users

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        users = validated_data["user_ids"]

        conversation = Conversation.objects.create(
            type=Conversation.TypeChoices.GROUP,
            title=validated_data["title"],
        )

        ConversationMember.objects.create(
            conversation=conversation,
            user=request.user,
            role=ConversationMember.RoleChoices.OWNER,
        )

        ConversationMember.objects.bulk_create([
            ConversationMember(
                conversation=conversation,
                user=user,
                role=ConversationMember.RoleChoices.MEMBER,
            )
            for user in users
        ])

        return conversation