from django.urls import path
from .views import InternalUserLastSeenView

urlpatterns = [
    path('<int:pk/last-seen/', InternalUserLastSeenView.as_view()),  
]