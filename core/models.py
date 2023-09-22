from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User model"""

    is_whitelisted = models.BooleanField(default=False)
    system_message = models.TextField(null=True, blank=True)
    summary_message = models.TextField(null=True, blank=True)
    iteration = models.PositiveIntegerField(default=0)

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


class Role(models.TextChoices):
    """Enum of message roles"""

    ASSISTANT = "A", "assistant"
    USER = "U", "user"
    SYSTEM = "S", "system"
    FUNCTION = "F", "function"


class Message(models.Model):
    """Message model"""

    timestamp = models.DateTimeField(auto_now_add=True)
    users = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=Role.choices)
    text = models.TextField()
    name = models.TextField(null=True, blank=True)


class Chatcmpl(models.Model):
    """Chat completion model"""

    id = models.TextField(primary_key=True, unique=True)
    users = models.ForeignKey(User, on_delete=models.CASCADE)
    object_name = models.TextField()
    created_at = models.DateTimeField()
    model = models.TextField()


class Choice(models.Model):
    """Message choice model given by Chatcmpl"""

    chatcmpl = models.ForeignKey(Chatcmpl, on_delete=models.CASCADE)
    index = models.PositiveIntegerField()
    message = models.OneToOneField(
        Message, null=True, blank=True, on_delete=models.CASCADE
    )
    finish_reason = models.TextField()
    completion_tokens = models.PositiveIntegerField()
    prompt_tokens = models.PositiveIntegerField()
