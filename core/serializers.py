from rest_framework import serializers

from .models import (
    Adventure,
    Knowledge,
    Message,
    Scene,
    SceneNpc,
    SceneRunner,
    User,
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""

    class Meta:
        model = User
        fields = "__all__"


class AdventureStatsSerializer(serializers.Serializer):
    """Serializer for the UserDetailsSerializer"""

    id = serializers.IntegerField()
    token_count = serializers.IntegerField()


class SceneNpcStatsSerializer(serializers.Serializer):
    """Serializer for the UserDetailsSerializer"""

    index = serializers.IntegerField()
    name = serializers.CharField()
    title = serializers.CharField()
    token_count = serializers.IntegerField()


class SceneRunnerStatsSerializer(serializers.Serializer):
    """Serializer for the UserDetailsSerializer"""

    id = serializers.IntegerField()
    name = serializers.CharField()
    npcs = serializers.ListField(child=SceneNpcStatsSerializer())
    token_count = serializers.IntegerField()


class UserDetailsSerializer(serializers.Serializer):
    """Serializer for the UserDetailsView"""

    num_adventures = serializers.IntegerField()
    token_count = serializers.IntegerField()
    adventures = serializers.ListField(child=AdventureStatsSerializer())
    scenes = serializers.ListField(child=SceneRunnerStatsSerializer())


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


class AdventureOwnedSerializer(serializers.ModelSerializer):
    """Serializer for only user owned the Adventure model"""

    class Meta:
        model = Adventure
        fields = "__all__"
        read_only_fields = ["user"]


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model"""

    class Meta:
        model = Message
        fields = "__all__"


class ConvoHistorySerializer(serializers.Serializer):
    """Serializer for the ConvoHistoryView"""

    history = serializers.ListField(child=MessageSerializer())


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


class KnowledgeSerializer(serializers.ModelSerializer):
    """Serializer for the Knowledge model"""

    class Meta:
        model = Knowledge
        fields = ["id", "name", "description"]


class SceneNpcSerializer(serializers.ModelSerializer):
    """Serializer for the SceneNpc model"""

    knowledges = serializers.ListSerializer(child=KnowledgeSerializer())

    class Meta:
        model = SceneNpc
        fields = ["id", "name", "title", "index", "knowledges"]
        depth = 1


class SceneSerializer(serializers.ModelSerializer):
    """Serializer for the SceneView"""

    npcs: serializers.ListField = serializers.ListSerializer(
        child=SceneNpcSerializer()
    )

    class Meta:
        model = Scene
        fields = ["id", "name", "npcs"]
        depth = 2


class SceneRunnerCreateSerializer(serializers.ModelSerializer):
    """Serializer for the SceneRunnerCreateView"""

    class Meta:
        model = SceneRunner
        fields = ["id"]
        read_only_fields = ["id"]
