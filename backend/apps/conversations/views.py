from rest_framework import generics
from .models import Conversation, ConversationMember
from .serializers import ConversationSerializer, ConversationMemberSerializer, PrivateConversationCreateSerializer, GroupConversationCreateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .permissions import (CanDeleteConversation, CanUpdateConversation, IsConversationMember, 
    CanChangeMemberRole, CanManageMembers, CanRemoveMember)
from config.pagination import ConversationCursorPagination



class ConversationListAPIView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    pagination_class = ConversationCursorPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(
            members__user=self.request.user
        ).distinct()
    

class ConversationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(
            members__user=self.request.user
        ).distinct()

    def get_permissions(self):
        if self.request.method == "GET":
            return [
                IsAuthenticated(),
                IsConversationMember(),
            ]

        if self.request.method in ["PUT", "PATCH"]:
            return [
                IsAuthenticated(),
                CanUpdateConversation(),
            ]

        if self.request.method == "DELETE":
            return [
                IsAuthenticated(),
                CanDeleteConversation(),
            ]

        return [IsAuthenticated()]
    

class ConversationMemberListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ConversationMemberSerializer

    def get_queryset(self):
        return ConversationMember.objects.filter(
            conversation_id=self.kwargs["conversation_id"]
        )

    def get_permissions(self):
        if self.request.method == "GET":
            return [
                IsAuthenticated(),
                IsConversationMember(),
            ]

        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                CanManageMembers(),
            ]

        return [IsAuthenticated()]

    

class ConversationMemberDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ConversationMemberSerializer

    def get_queryset(self):
        return ConversationMember.objects.filter(
            conversation_id=self.kwargs["conversation_id"]
        )

    def get_permissions(self):
        if self.request.method == "GET":
            return [
                IsAuthenticated(),
                IsConversationMember(),
            ]

        if self.request.method in ["PUT", "PATCH"]:
            return [
                IsAuthenticated(),
                CanChangeMemberRole(),
            ]

        if self.request.method == "DELETE":
            return [
                IsAuthenticated(),
                CanRemoveMember(),
            ]

        return [IsAuthenticated()]
        


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