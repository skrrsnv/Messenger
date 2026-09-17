from django.urls import path
from .views import (ConversationListAPIView, ConversationDetailAPIView, ConversationMemberListCreateAPIView,
ConversationMemberDetailAPIView, PrivateConversationCreateAPIView, GroupConversationCreateAPIView)

urlpatterns = [
    path('', ConversationListAPIView.as_view()),
    path("private/", PrivateConversationCreateAPIView.as_view()),
    path("group/", GroupConversationCreateAPIView.as_view()),
    path('<int:pk>/', ConversationDetailAPIView.as_view()),
    path('<int:conversation_id>/members/', ConversationMemberListCreateAPIView.as_view()),
    path('<int:conversation_id>/members/<int:pk>/', ConversationMemberDetailAPIView.as_view()),
]
