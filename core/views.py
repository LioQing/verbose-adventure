from rest_framework import generics, permissions, response, views, viewsets

from rest_auth.permissions import IsWhitelisted

from . import models, serializers


class UserView(
    generics.CreateAPIView,
    generics.RetrieveAPIView,
    generics.ListAPIView,
    generics.DestroyAPIView,
    generics.UpdateAPIView,
    viewsets.GenericViewSet,
):
    """Viewset for the User model"""

    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAdminUser]


class PingPongView(views.APIView):
    """View for checking if the server is running"""

    serializer_class = serializers.PingPongSerializer
    permission_classes = [IsWhitelisted]

    def get(self, request):
        """Return a pong response"""
        serializer = self.serializer_class(data={"ping": "pong"})
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data)


class AdventureView(
    generics.CreateAPIView,
    generics.RetrieveAPIView,
    generics.ListAPIView,
    generics.UpdateAPIView,
    viewsets.GenericViewSet,
):
    """View for the adventure"""

    queryset = models.Adventure.objects.all()
    serializer_class = serializers.AdventureSerializer
    permission_classes = [IsWhitelisted]


class AdventureStartView(views.APIView):
    """View for initializing the story"""

    serializer_class = serializers.AdventureStartSerializer
    permission_classes = [IsWhitelisted]

    def get(self, request):
        """Return first API response of the story"""
        pass
