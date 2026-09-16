from django.urls import path
from .views import ConversationListCreateAPIView, ConversationDetailAPIView

urlpatterns = [
    path('', ConversationListCreateAPIView.as_view()),
    path('<int:pk>/', ConversationDetailAPIView.as_view()),
]
