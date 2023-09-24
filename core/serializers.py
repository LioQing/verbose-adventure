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


class AdventureOwnedSerializer(serializers.ModelSerializer):
    """Serializer for only user owned the Adventure model"""

    class Meta:
        model = Adventure
        fields = "__all__"
        read_only_fields = ["user"]


class ConvoStartSerializer(serializers.Serializer):
    """Serializer for the ConvoStartView"""

    response = serializers.CharField(read_only=True)


class ConvoRespondSerializer(serializers.Serializer):
    """Serializer for the ConvoRespondView"""

    user_response = serializers.CharField(required=True)
    api_response = serializers.CharField(read_only=True)
    summary = serializers.CharField(read_only=True)


class ConvoSummarySerializer(serializers.Serializer):
    """Serializer for the ConvoSummaryView"""

    summary = serializers.CharField()


class ConvoTokenCountSerializer(serializers.Serializer):
    """Serializer for the ConvoTokenCountView"""

    token_count = serializers.IntegerField()
