from django.urls import path
from .views import InternalConversationMembershipAPIView
from apps.messaging.views import InternalMessageCreateAPIView

urlpatterns = [
    path("<int:conversation_id>/members/<int:user_id>/", InternalConversationMembershipAPIView.as_view(),),
    path("<int:conversation_id>/messages/", InternalMessageCreateAPIView.as_view(),), 
]