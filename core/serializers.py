from rest_framework import serializers

from .models import Adventure, User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""

    class Meta:
        model = User
        fields = "__all__"


class PingPongSerializer(serializers.Serializer):
    """Serializer for the PingPongView"""

    ping = serializers.CharField(max_length=4)


class AdventureSerializer(serializers.ModelSerializer):
    """Serializer for the Adventure model"""

    class Meta:
        model = Adventure
        fields = "__all__"


class AdventureStartSerializer(serializers.Serializer):
    """Serializer for the AdventureStartView"""

    response = serializers.CharField()
