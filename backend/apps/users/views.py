from rest_framework import generics, status
from .models import User
from apps.conversations.models import ConversationMember
from .serializers import UserSerializer, RegisterSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from .internal_permissions import HasInternalAPIToken
from django.contrib.auth import get_user_model


User = get_user_model()


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    

class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    

class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    

class LoginAPIView(TokenObtainPairView):
    permission_classes = [AllowAny]
    

class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid or blacklisted refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK,
        )   
        
        
class InternalTokenValidationAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        return Response({
            "user_id": request.user.id,
        })


class InternalUserLastSeenView(APIView):
    permission_classes = [HasInternalAPIToken]
    authentication_classes = [JWTAuthentication]

    def post(self, request, user_id: int):
        last_seen = timezone.now()

        updated = User.objects.filter(pk=user_id).update(
            last_seen=last_seen,
        )

        if not updated:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"last_seen": last_seen.isoformat()},
            status=status.HTTP_200_OK,
        )


class InternalUserConversationsAPIView(APIView):
    authentication_classes = []
    permission_classes = [HasInternalAPIToken]

    def get(self, request, user_id: int):
        conversation_ids = list(
            ConversationMember.objects.filter(
                user_id=user_id,
            ).values_list(
                "conversation_id",
                flat=True,
            ).distinct()
        )

        return Response({
            "conversation_ids": conversation_ids,
        })