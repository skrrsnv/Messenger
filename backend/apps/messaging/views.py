from rest_framework import generics, status
from .models import Message, MessageRead
from .serializers import MessageSerializer, MessageReadSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsMessageSender
from apps.conversations.permissions import IsConversationMember
from config.pagination import MessageCursorPagination
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from apps.users.internal_permissions import HasInternalAPIToken
from apps.conversations.models import ConversationMember
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from apps.conversations.events import publish_message_created
from django.utils import timezone
from .models import MessageDelivery
from .events import publish_message_event
from .statuses import advance_message_status


class MessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    pagination_class = MessageCursorPagination
    permission_classes = [IsAuthenticated, IsConversationMember,]
    def get_queryset(self):
        return Message.objects.filter(
            conversation_id=self.kwargs["conversation_id"]
        )

    def perform_create(self, serializer):
        serializer.save(
            sender=self.request.user,
            conversation_id=self.kwargs["conversation_id"],
        )


class MessageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(
            conversation_id=self.kwargs["conversation_id"]
        )

    def get_permissions(self):
        if self.request.method == "GET":
            return [
                IsAuthenticated(),
                IsConversationMember(),
            ]

        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [
                IsAuthenticated(),
                IsConversationMember(),
                IsMessageSender(),
            ]

        return [IsAuthenticated()]
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
        

class MessageReadCreateAPIView(generics.CreateAPIView):
    serializer_class = MessageReadSerializer
    permission_classes = [IsAuthenticated, IsConversationMember]
    
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            message = get_object_or_404(
                Message.objects.select_for_update(),
                pk=kwargs["message_id"],
                conversation_id=kwargs["conversation_id"],
            )

            if message.sender_id == request.user.id:
                return Response(
                    {"detail": "You cannot mark your own message as read."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            now = timezone.now()

            delivery, delivery_created = (
                MessageDelivery.objects.get_or_create(
                    message=message,
                    user=request.user,
                    defaults={"delivered_at": now},
                )
            )

            if delivery.delivered_at is None:
                delivery.delivered_at = now
                delivery.save(update_fields=["delivered_at"])
                delivery_created = True

            message_read, read_created = (
                MessageRead.objects.get_or_create(
                    message=message,
                    user=request.user,
                )
            )

            if delivery_created:
                delivered_event = {
                    "type": "message.delivered",
                    "conversation_id": message.conversation_id,
                    "message_id": message.id,
                    "user_id": request.user.id,
                    "status": "delivered",
                    "delivered_at": delivery.delivered_at.isoformat(),
                }
                transaction.on_commit(
                    lambda event=delivered_event:
                        publish_message_event(event)
                )

            if read_created:
                read_event = {
                    "type": "message.read",
                    "conversation_id": message.conversation_id,
                    "message_id": message.id,
                    "user_id": request.user.id,
                    "status": "read",
                    "read_at": message_read.read_at.isoformat(),
                }
                transaction.on_commit(
                    lambda event=read_event:
                        publish_message_event(event)
                )

            advance_message_status(message, Message.STATUS_READ)

            serializer = self.get_serializer(message_read)

        return Response(
            serializer.data,
            status=(
                status.HTTP_201_CREATED
                if read_created
                else status.HTTP_200_OK
            ),
        )
        

class InternalMessageCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasInternalAPIToken, IsAuthenticated]

    def post(self, request, conversation_id):
        user_id = request.user.id
        text = request.data.get("text")

        if not isinstance(text, str) or not text.strip():
            return Response(
                {"detail": "Message text cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_member = ConversationMember.objects.filter(
            conversation_id=conversation_id,
            user_id=user_id,
        ).exists()

        if not is_member:
            return Response(
                {"detail": "User is not a conversation member."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = MessageSerializer(
            data={"text": text.strip()},
        )
        serializer.is_valid(raise_exception=True)

        message = Message.objects.create(
            conversation_id=conversation_id,
            sender_id=user_id,
            text=serializer.validated_data["text"],
        )

        event = {
            "type": "message.created",
            "conversation_id": message.conversation_id,
            "data": {
                "id": message.id,
                "conversation": message.conversation_id,
                "sender": message.sender_id,
                "text": message.text,
                "created_at": message.created_at.isoformat(),
            },
        }

        sent_event = {
            "type": "message.sent",
            "conversation_id": message.conversation_id,
            "message_id": message.id,
            "user_id": user_id,
            "status": "sent",
            "created_at": message.created_at.isoformat(),
        }

        def publish_events():
            publish_message_created(event)
            publish_message_event(sent_event)

        transaction.on_commit(publish_events)

        return Response(
            event["data"],
            status=status.HTTP_201_CREATED,
        )
        

class MessageDeliveryCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsConversationMember,]

    def post(self, request, conversation_id, message_id):
        with transaction.atomic():
            message = get_object_or_404(
                Message.objects.select_for_update(),
                pk=message_id,
                conversation_id=conversation_id,
            )

            if message.sender_id == request.user.id:
                return Response(
                    {"detail": "You cannot acknowledge delivery of your own message."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            delivery, created = MessageDelivery.objects.get_or_create(
                message=message,
                user=request.user,
                defaults={"delivered_at": timezone.now()},
            )

            if delivery.delivered_at is None:
                delivery.delivered_at = timezone.now()
                delivery.save(update_fields=["delivered_at"])
                created = True

            status_changed = advance_message_status(
                message,
                Message.STATUS_DELIVERED,
            )

            if created:
                event = {
                    "type": "message.delivered",
                    "conversation_id": conversation_id,
                    "message_id": message.id,
                    "user_id": request.user.id,
                    "status": "delivered",
                    "delivered_at": delivery.delivered_at.isoformat(),
                }
                transaction.on_commit(
                    lambda event=event: publish_message_event(event)
                )

        return Response(
            {
                "message_id": message.id,
                "user_id": request.user.id,
                "status": message.status,
                "delivered_at": delivery.delivered_at,
            },
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )