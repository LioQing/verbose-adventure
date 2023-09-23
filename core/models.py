from django.contrib.auth.models import AbstractUser
from django.db import models

from config.adventure import adventure_config


class User(AbstractUser):
    """User model"""

    is_whitelisted = models.BooleanField(default=False)

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


class Role(models.TextChoices):
    """Enum of message roles"""

    ASSISTANT = "A", "Assistant"
    USER = "U", "User"
    SYSTEM = "S", "System"
    FUNCTION = "F", "Function"


class ChatcmplKind(models.TextChoices):
    """Enum of chat completion kinds"""

    MESSAGE = "M", "Message"
    SUMMARY = "S", "Summary"


class Summary(models.Model):
    """Summary model"""

    summary = models.TextField()


class Adventure(models.Model):
    """Adventure model"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    summary = models.OneToOneField(
        Summary,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    system_message = models.TextField(default=adventure_config.system_message)
    start_message = models.TextField(default=adventure_config.start_message)
    iteration = models.PositiveIntegerField(default=0)


class Message(models.Model):
    """Message model"""

    timestamp = models.DateTimeField(auto_now_add=True)
    adventure = models.ForeignKey(Adventure, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=Role.choices)
    content = models.TextField()
    name = models.TextField(null=True, blank=True)


class Chatcmpl(models.Model):
    """Chat completion model"""

    id = models.TextField(primary_key=True, unique=True)
    adventure = models.ForeignKey(Adventure, on_delete=models.CASCADE)
    summary = models.ForeignKey(
        Summary, null=True, blank=True, on_delete=models.CASCADE
    )
    messages = models.ManyToManyField(Message)
    kind = models.CharField(max_length=1, choices=ChatcmplKind.choices)
    object_name = models.TextField()
    created_at = models.DateTimeField()
    model = models.TextField()
    completion_tokens = models.PositiveIntegerField()
    prompt_tokens = models.PositiveIntegerField()


class Choice(models.Model):
    """Message choice model given by Chatcmpl"""

    chatcmpls = models.ForeignKey(Chatcmpl, on_delete=models.CASCADE)
    index = models.PositiveIntegerField()
    message = models.OneToOneField(
        Message, null=True, blank=True, on_delete=models.CASCADE
    )
    summary = models.OneToOneField(
        Summary, null=True, blank=True, on_delete=models.CASCADE
    )
    finish_reason = models.TextField()
