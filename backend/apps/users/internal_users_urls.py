from django.urls import path
from .views import InternalUserLastSeenView, InternalUserConversationsAPIView

urlpatterns = [
    path('<int:user_id>/last-seen/', InternalUserLastSeenView.as_view()),
    path('<int:user_id>/conversations/', InternalUserConversationsAPIView.as_view()),  
]