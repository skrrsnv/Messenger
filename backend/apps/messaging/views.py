from rest_framework import generics
from .models import Message
from .serializers import MessageSerializer
from rest_framework.permissions import IsAuthenticated


class MessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Message.objects.filter(
            conversation_id=self.kwargs["conversation_id"]
        )

    def perform_create(self, serializer):
        serializer.save(
            sender=self.request.user,
            conversation_id=self.kwargs["conversation_id"],
        )
    

class MessageDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Message.objects.filter(
            conversation_id=self.kwargs["conversation_id"]
        )