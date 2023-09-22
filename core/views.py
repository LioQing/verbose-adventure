from rest_framework import generics, permissions, response, viewsets

from . import serializers
from .models import User


class UserView(
    generics.CreateAPIView,
    generics.RetrieveAPIView,
    generics.ListAPIView,
    generics.DestroyAPIView,
    generics.UpdateAPIView,
    viewsets.GenericViewSet,
):
    """Viewset for the User model"""

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAdminUser]


class PingPongView(generics.GenericAPIView):
    """View for checking if the server is running"""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Return a pong response"""
        return response.Response({"ping": "pong"})
