from typing import List

from pydantic import BaseModel


class Knowledge(BaseModel):
    """Class for knowledge base."""

    name: str
    description: str
    knowledge: str


class SceneNpc(BaseModel):
    """Class for scene NPC."""

    name: str
    title: str
    character: str
    knowledges: List[Knowledge]


class Scene(BaseModel):
    """Class for scene."""

    name: str
    system_message: str
    npcs: List[SceneNpc]
