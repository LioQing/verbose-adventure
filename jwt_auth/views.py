from rest_framework import permissions
from rest_framework_simplejwt import views as jwt_views

from . import serializers


class ObtainTokenPairView(jwt_views.TokenObtainPairView):
    """Obtain access and refresh token pair"""

    serializer_class = serializers.TokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
