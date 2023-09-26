from rest_framework import serializers

from .models import Adventure, Message, User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""

    class Meta:
        model = User
        fields = "__all__"


class AdventureStatsSerializer(serializers.Serializer):
    """Serializer for the UserDetailsSerializer"""

    id = serializers.IntegerField()
    token_count = serializers.IntegerField()


class UserDetailsSerializer(serializers.Serializer):
    """Serializer for the UserDetailsView"""

    num_adventures = serializers.IntegerField()
    token_count = serializers.IntegerField()
    adventures = serializers.ListField(child=AdventureStatsSerializer())


class WhitelistSerializer(serializers.Serializer):
    """Serializer for the WhitelistView"""

    username = serializers.CharField(required=True)


class PingPongSerializer(serializers.Serializer):
    """Serializer for the PingPongView"""

    ping = serializers.CharField(max_length=4)


class AdventureSerializer(serializers.ModelSerializer):
    """Serializer for the Adventure model"""

    class Meta:
        model = Adventure
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model"""

    class Meta:
        model = Message
        fields = "__all__"


class ConvoHistorySerializer(serializers.Serializer):
    """Serializer for the ConvoHistoryView"""

    history = serializers.ListField(child=MessageSerializer())


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
    summary = serializers.CharField(read_only=True, allow_blank=True)


class ConvoSummarySerializer(serializers.Serializer):
    """Serializer for the ConvoSummaryView"""

    summary = serializers.CharField()


class ConvoTokenCountSerializer(serializers.Serializer):
    """Serializer for the ConvoTokenCountView"""

    token_count = serializers.IntegerField()
