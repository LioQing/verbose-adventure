from rest_framework import permissions
from rest_framework_simplejwt import views as jwt_views


class ObtainTokenPairView(jwt_views.TokenObtainPairView):
    """Obtain access and refresh token pair"""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """Return access and refresh token pair"""
        return super().post(request, *args, **kwargs)


class TokenRefreshView(jwt_views.TokenRefreshView):
    """Refresh access token"""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """Return access token"""
        return super().post(request, *args, **kwargs)
