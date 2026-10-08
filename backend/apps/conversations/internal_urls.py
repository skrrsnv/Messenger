from django.urls import path
from .views import InternalConversationMembershipAPIView

urlpatterns = [
    path("<int:conversation_id>/members/<int:user_id>/", InternalConversationMembershipAPIView.as_view(),),
]