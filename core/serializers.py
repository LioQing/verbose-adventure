from rest_framework import serializers

from .models import User


class PingPongSerializer(serializers.Serializer):
    """Serializer for the PingPongView"""

    ping = serializers.CharField(max_length=4)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""

    class Meta:
        model = User
        fields = "__all__"
