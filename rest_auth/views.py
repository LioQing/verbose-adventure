from drf_yasg.utils import swagger_auto_schema
from rest_framework import parsers, permissions, status
from rest_framework_simplejwt import views as jwt_views

from .serializers import (
    TokenObtainPairResponseSerializer, TokenObtainPairSerializer
)


class ObtainTokenPairView(jwt_views.TokenObtainPairView):
    """Obtain access and refresh token pair"""

    serializer_class = TokenObtainPairSerializer
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TokenObtainPairResponseSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        """Return access and refresh token pair"""
        return super().post(request, *args, **kwargs)


class TokenRefreshView(jwt_views.TokenRefreshView):
    """Refresh access token"""

    parser_classes = [parsers.FormParser]

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TokenObtainPairResponseSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        """Return access token"""
        return super().post(request, *args, **kwargs)
