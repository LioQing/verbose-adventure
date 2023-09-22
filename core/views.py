from drf_yasg.utils import swagger_auto_schema
from rest_framework import (
    generics, parsers, permissions, response, status, views, viewsets
)

from rest_auth.permissions import IsWhitelisted

from .models import User
from .serializers import PingPongSerializer, UserSerializer

# ---------------- User ----------------


class UserView(
    generics.CreateAPIView,
    generics.RetrieveAPIView,
    generics.ListAPIView,
    viewsets.GenericViewSet,
):
    """Viewset for the User model"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]
    permission_classes = [permissions.IsAdminUser]


class ModifyUserView(
    generics.DestroyAPIView,
    generics.UpdateAPIView,
    viewsets.GenericViewSet,
):
    """Viewset for modifying the User model"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


# ---------------- Ping ----------------


class PingPongView(views.APIView):
    """View for checking if the server is running"""

    serializer_class = PingPongSerializer
    permission_classes = [IsWhitelisted]

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: PingPongSerializer,
        }
    )
    def get(self, request):
        """Return a pong response"""
        serializer = self.serializer_class(data={"ping": "pong"})
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data)


# ---------------- Convo ----------------
