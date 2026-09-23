from rest_framework import generics
from .models import Message
from .serializers import MessageSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsMessageSender
from apps.conversations.permissions import IsConversationMember


class MessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
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