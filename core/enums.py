from __future__ import annotations

from django.db import models

from engine import models as engine_models


class Role(models.TextChoices):
    """Enum of message roles"""

    ASSISTANT = "A", "Assistant"
    USER = "U", "User"
    SYSTEM = "S", "System"
    FUNCTION = "F", "Function"

    @classmethod
    def from_engine_role(self, role: engine_models.Role) -> str:
        """
        Create a role string from an engine Role

        Args:
            role: The engine Role

        Returns:
            The created role string
        """
        return ENGINE_TO_CORE_ROLE[role]

    @classmethod
    def to_engine_role(self, role: Role) -> engine_models.Role:
        """
        Create an engine Role from a role string

        Args:
            role: The role string

        Returns:
            The created engine Role
        """
        return CORE_TO_ENGINE_ROLE[role]


ENGINE_TO_CORE_ROLE = {
    engine_models.Role.ASSISTANT: Role.ASSISTANT,
    engine_models.Role.USER: Role.USER,
    engine_models.Role.SYSTEM: Role.SYSTEM,
    engine_models.Role.FUNCTION: Role.FUNCTION,
}

CORE_TO_ENGINE_ROLE = {
    Role.ASSISTANT: engine_models.Role.ASSISTANT,
    Role.USER: engine_models.Role.USER,
    Role.SYSTEM: engine_models.Role.SYSTEM,
    Role.FUNCTION: engine_models.Role.FUNCTION,
}


class ChatcmplKind(models.TextChoices):
    """Enum of chat completion kinds"""

    MESSAGE = "M", "Message"
    SUMMARY = "S", "Summary"
