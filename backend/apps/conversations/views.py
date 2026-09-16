from rest_framework import generics
from .models import Conversation
from .serializers import ConversationSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated

class ConversationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    

class ConversationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]