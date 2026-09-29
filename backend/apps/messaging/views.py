from rest_framework import generics
from .models import Message, MessageRead
from .serializers import MessageSerializer, MessageReadSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsMessageSender
from apps.conversations.permissions import IsConversationMember
from config.pagination import MessageCursorPagination
from django.shortcuts import get_object_or_404


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
        message = get_object_or_404(
            Message,
            pk=kwargs["message_id"],
            conversation_id=kwargs["conversation_id"],
        )

        message_read, created = MessageRead.objects.get_or_create(
            message=message,
            user=request.user,
        )

        serializer = self.get_serializer(message_read)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )