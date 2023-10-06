import inspect
from typing import Any, Dict, List

from pydantic import BaseModel, Field, validator


class Knowledge(BaseModel):
    """Class for knowledge base."""

    name: str
    description: str
    knowledge: str
    id: str = Field(
        default_factory=lambda: inspect.getmodule(
            inspect.stack()[2][0]
        ).__name__
    )

    @validator("id", always=True)
    def validate_id(cls, v: str, values: Dict[str, Any]) -> str:
        """Validate id."""
        return f"{v}_{values['name']}"


class SceneNpc(BaseModel):
    """Class for scene NPC."""

    name: str
    title: str
    character: str
    knowledges: List[Knowledge]
    id: str = Field(
        default_factory=lambda: inspect.getmodule(
            inspect.stack()[2][0]
        ).__name__
    )

    @validator("id", always=True)
    def validate_id(cls, v: str, values: Dict[str, Any]) -> str:
        """Validate id."""
        return f"{v}_{values['name']}_{values['title']}"


class Scene(BaseModel):
    """Class for scene."""

    name: str
    system_message: str
    npcs: List[SceneNpc]
    id: str = Field(
        default_factory=lambda: inspect.getmodule(
            inspect.stack()[2][0]
        ).__name__
    )
