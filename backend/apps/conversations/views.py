from rest_framework import generics
from rest_framework.views import APIView
from .models import Conversation, ConversationMember
from .serializers import ConversationSerializer, ConversationMemberSerializer, PrivateConversationCreateSerializer, GroupConversationCreateSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status



class ConversationListAPIView(generics.ListAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    

class ConversationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    

class ConversationMemberListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ConversationMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ConversationMember.objects.filter(conversation_id=self.kwargs['conversation_id'])
    

class ConversationMemberDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ConversationMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
            return ConversationMember.objects.filter(conversation_id=self.kwargs['conversation_id'])
        


class PrivateConversationCreateAPIView(generics.CreateAPIView):
    serializer_class = PrivateConversationCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation = serializer.save()

        return Response(
            ConversationSerializer(
                conversation,
                context={"request": request},
            ).data,
            status=201,
        )


class GroupConversationCreateAPIView(generics.CreateAPIView):
    serializer_class = GroupConversationCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation = serializer.save()

        return Response(
            ConversationSerializer(
                conversation,
                context={"request": request},
            ).data,
            status=201,
        )