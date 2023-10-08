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
        ).__name__.replace(".", "-")
    )

    @validator("id", always=True)
    def validate_id(cls, v: str, values: Dict[str, Any]) -> str:
        """Validate id."""
        postfix = f"-{values['name']}"
        if v.endswith(postfix):
            return v
        return f"{v}{postfix}"


class SceneNpc(BaseModel):
    """Class for scene NPC."""

    name: str
    title: str
    character: str
    knowledges: List[Knowledge]
    id: str = Field(
        default_factory=lambda: inspect.getmodule(
            inspect.stack()[2][0]
        ).__name__.replace(".", "-")
    )

    @validator("id", always=True)
    def validate_id(cls, v: str, values: Dict[str, Any]) -> str:
        """Validate id."""
        postfix = f"-{values['name']}-{values['title']}"
        if v.endswith(postfix):
            return v
        return f"{v}{postfix}"


class Scene(BaseModel):
    """Class for scene."""

    name: str
    system_message: str
    npcs: List[SceneNpc]
    id: str = Field(
        default_factory=lambda: inspect.getmodule(
            inspect.stack()[2][0]
        ).__name__.replace(".", "-")
    )
