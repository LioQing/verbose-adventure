from __future__ import annotations

from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db import models

import data.scene
from config.adventure import adventure_config
from engine import models as engine_models

from . import enums, managers


class User(AbstractUser):
    """User model"""

    is_whitelisted = models.BooleanField(default=False)

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


class Summary(models.Model):
    """Summary model"""

    summary = models.TextField()

    objects = managers.SummaryManager()

    def from_engine_summary(
        adventure: Adventure, summary: engine_models.Message
    ) -> Summary:
        """
        Create a Summary from an engine Summary

        Args:
            adventure: The adventure
            summary: The engine summary Message

        Returns:
            The created Summary
        """
        return Summary(
            summary=summary.content,
        )


class Adventure(models.Model):
    """Adventure model"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    summary = models.OneToOneField(
        Summary,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    latest_message = models.OneToOneField(
        "Message",
        related_name="latest_adventure",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    system_message = models.TextField(
        default=adventure_config.system_message, blank=True
    )
    start_message = models.TextField(
        default=adventure_config.start_message, blank=True
    )
    iteration = models.PositiveIntegerField(default=0, blank=True)

    @property
    def token_count(self) -> int:
        """
        Return the total token count of the adventure

        Returns:
            The total token count of the adventure
        """
        return (
            self.chatcmpl_set.annotate(
                token=models.F("completion_tokens") + models.F("prompt_tokens")
            ).aggregate(models.Sum("token"))["token__sum"]
            or 0
        )


class Scene(models.Model):
    """Scene model"""

    id = models.TextField(primary_key=True, unique=True)
    name = models.TextField()
    system_message = models.TextField()

    # Backward typehint
    npcs: models.QuerySet[SceneNpc]

    objects = managers.SceneManager()

    def from_scene_data(scene_data: data.scene.Scene) -> Scene:
        """
        Create a Scene from an engine Scene

        Args:
            scene_data: The engine Scene

        Returns:
            The created Scene
        """
        return Scene(
            id=scene_data.id,
            name=scene_data.name,
            system_message=scene_data.system_message,
        )

    def to_scene_data(self) -> data.scene.Scene:
        """
        Create an engine Scene from a Scene

        Args:
            scene: The Scene

        Returns:
            The created engine Scene
        """
        return data.scene.Scene(
            id=self.id,
            name=self.name,
            system_message=self.system_message,
            npcs=[npc.to_scene_data_npc() for npc in self.npcs.all()],
        )


class Knowledge(models.Model):
    """Knowledge model"""

    id = models.TextField(primary_key=True, unique=True)
    name = models.TextField()
    description = models.TextField()
    knowledge = models.TextField()

    # Backward typehint
    npcs: models.QuerySet[SceneNpc]

    def from_scene_data_knowledge(
        knowledge: data.scene.Knowledge,
    ) -> Knowledge:
        """
        Create a Knowledge from an engine Knowledge

        Args:
            knowledge: The engine Knowledge

        Returns:
            The created Knowledge
        """
        return Knowledge(
            id=knowledge.id,
            name=knowledge.name,
            description=knowledge.description,
            knowledge=knowledge.knowledge,
        )

    def to_scene_data_knowledge(self) -> data.scene.Knowledge:
        """
        Create an engine Knowledge from a Knowledge

        Args:
            knowledge: The Knowledge

        Returns:
            The created engine Knowledge
        """
        return data.scene.Knowledge(
            id=self.id,
            name=self.name,
            description=self.description,
            knowledge=self.knowledge,
        )


class SceneNpc(models.Model):
    """Scene NPC model"""

    id = models.TextField(primary_key=True, unique=True)
    name = models.TextField()
    title = models.TextField()
    character = models.TextField()
    knowledges = models.ManyToManyField(Knowledge, related_name="npcs")
    scene = models.ForeignKey(
        Scene, related_name="npcs", on_delete=models.CASCADE
    )
    index = models.PositiveIntegerField()

    def from_scene_data_npc(
        npc: data.scene.SceneNpc, scene: Scene, index: int
    ) -> SceneNpc:
        """
        Create a SceneNpc from an engine SceneNpc with empty knowledge

        Args:
            npc: The engine SceneNpc
            scene: The engine Scene
            index: The index of the NPC

        Returns:
            The created SceneNpc
        """
        npc = SceneNpc(
            id=npc.id,
            name=npc.name,
            title=npc.title,
            character=npc.character,
            scene=scene,
            index=index,
        )
        return npc

    def to_scene_data_npc(self) -> data.scene.SceneNpc:
        """
        Create an engine SceneNpc from a SceneNpc

        Args:
            npc: The SceneNpc

        Returns:
            The created engine SceneNpc
        """
        return data.scene.SceneNpc(
            id=self.id,
            name=self.name,
            title=self.title,
            character=self.character,
            knowledges=[
                knowledge.to_scene_data_knowledge()
                for knowledge in self.knowledges.all()
            ],
        )


class SceneRunner(models.Model):
    """Scene runner model"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)

    # Backward typehint
    scenenpcadventurepair_set: models.QuerySet[SceneNpcAdventurePair]


class SceneNpcAdventurePair(models.Model):
    """Scene NPC adventure pair model"""

    runner = models.ForeignKey(SceneRunner, on_delete=models.CASCADE)
    npc = models.ForeignKey(SceneNpc, on_delete=models.CASCADE)
    adventure = models.OneToOneField(Adventure, on_delete=models.CASCADE)
    knowledge_selection_token_count = models.PositiveIntegerField(default=0)


class Message(models.Model):
    """Message model"""

    timestamp = models.DateTimeField(auto_now_add=True)
    adventure = models.ForeignKey(Adventure, on_delete=models.CASCADE)
    prev = models.OneToOneField(
        "Message",
        related_name="next",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    role = models.CharField(max_length=1, choices=enums.Role.choices)
    content = models.TextField()
    name = models.TextField(null=True, blank=True)

    objects = managers.MessageManager()

    def from_engine_message(
        adventure: Adventure, message: engine_models.Message
    ) -> Message:
        """
        Create a Message from an engine Message

        Args:
            adventure: The adventure
            message: The engine Message

        Returns:
            The created Message
        """
        prev = Adventure.objects.get(id=adventure.id).latest_message

        return Message(
            adventure=adventure,
            prev=prev,
            role=enums.Role.from_engine_role(message.role),
            content=message.content,
            name=message.name,
        )

    def to_engine_message(self) -> engine_models.Message:
        """
        Create an engine Message from a Message

        Args:
            message: The Message

        Returns:
            The created engine Message
        """
        return engine_models.Message(
            role=enums.Role.to_engine_role(self.role),
            content=self.content,
            name=self.name,
        )


class Chatcmpl(models.Model):
    """Chat completion model"""

    id = models.TextField(primary_key=True, unique=True)
    adventure = models.ForeignKey(Adventure, on_delete=models.CASCADE)
    summary = models.ForeignKey(
        Summary, null=True, blank=True, on_delete=models.CASCADE
    )
    messages = models.ManyToManyField(Message)
    kind = models.CharField(max_length=1, choices=enums.ChatcmplKind.choices)
    object_name = models.TextField()
    created_at = models.DateTimeField()
    model = models.TextField()
    completion_tokens = models.PositiveIntegerField()
    prompt_tokens = models.PositiveIntegerField()

    objects = managers.ChatcmplManager()


class Choice(models.Model):
    """Message choice model given by Chatcmpl"""

    chatcmpl = models.ForeignKey(Chatcmpl, on_delete=models.CASCADE)
    index = models.PositiveIntegerField()
    message = models.OneToOneField(
        Message, null=True, blank=True, on_delete=models.CASCADE
    )
    summary = models.OneToOneField(
        Summary, null=True, blank=True, on_delete=models.CASCADE
    )
    finish_reason = models.TextField()

    objects = managers.ChoiceManager()

    def from_engine_choice(
        chatcmpl: Chatcmpl,
        message: Optional[Message],
        summary: Optional[Summary],
        choice: engine_models.Choice,
    ) -> Choice:
        """
        Create a Choice from an engine Choice

        Args:
            adventure: The adventure
            message: The message
            summary: The summary
            choice: The engine Choice

        Returns:
            The created Choice
        """
        return Choice(
            chatcmpl=chatcmpl,
            index=choice.index,
            message=message,
            summary=summary,
            finish_reason=choice.finish_reason,
        )
