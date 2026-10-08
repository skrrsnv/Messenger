from django.urls import path
from .views import InternalTokenValidationAPIView

urlpatterns = [
    path('', InternalTokenValidationAPIView.as_view()),  
]