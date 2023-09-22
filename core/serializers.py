from rest_framework import serializers

from .models import User


class PingPongSerializer(serializers.Serializer):
    """Serializer for the PingPongView"""

    pass


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""

    class Meta:
        model = User
        fields = "__all__"
