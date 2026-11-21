from django.contrib.auth import logout
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.api.serializers import (
    AuthTokenSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)
from apps.accounts.models import User
from apps.accounts.services import issue_token, revoke_tokens


def _token_response(user: User, *, status_code: int) -> Response:
    token = issue_token(user)
    payload = AuthTokenSerializer({"token": token.key, "user": user}).data
    return Response(payload, status=status_code)


class PublicAuthView(APIView):
    authentication_classes: list = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class RegisterView(PublicAuthView):
    @extend_schema(request=RegisterSerializer, responses={201: AuthTokenSerializer})
    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return _token_response(user, status_code=status.HTTP_201_CREATED)


class LoginView(PublicAuthView):
    @extend_schema(request=LoginSerializer, responses={200: AuthTokenSerializer})
    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return _token_response(serializer.validated_data["user"], status_code=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={204: OpenApiResponse(description="Déconnecté.")})
    def post(self, request: Request) -> Response:
        revoke_tokens(request.user)
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user
