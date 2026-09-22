from django.urls import path
from .views import (ConversationListAPIView, ConversationDetailAPIView, ConversationMemberListCreateAPIView,
ConversationMemberDetailAPIView, PrivateConversationCreateAPIView, GroupConversationCreateAPIView)
from apps.messaging.views import MessageListCreateAPIView, MessageDetailAPIView

urlpatterns = [
    path('', ConversationListAPIView.as_view()),
    path("private/", PrivateConversationCreateAPIView.as_view()),
    path("group/", GroupConversationCreateAPIView.as_view()),
    path('<int:pk>/', ConversationDetailAPIView.as_view()),
    path('<int:conversation_id>/members/', ConversationMemberListCreateAPIView.as_view()),
    path('<int:conversation_id>/members/<int:pk>/', ConversationMemberDetailAPIView.as_view()),
    path('<int:conversation_id>/messages/', MessageListCreateAPIView.as_view()),
    path('<int:conversation_id>/messages/<int:pk>', MessageDetailAPIView.as_view())
]
