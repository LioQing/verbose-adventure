import logging
from typing import Callable, List, Optional, Tuple

from config.adventure import adventure_config
from data.scene import SceneNpc
from engine.scene import BaseSceneCoupler

from ..adventure import Adventure


class SceneCoupler(BaseSceneCoupler):
    """The concrete SceneCoupler implementation."""

    logger: logging.Logger
    adventures: List[Tuple[Adventure, SceneNpc]]

    def __init__(self, adventures: List[Adventure] = []):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(adventure_config.log_level)
        self.adventures = adventures

    def get_adventure(self, index: int) -> Optional[Callable]:
        """
        Gets the function of the NPC to run the user flow at this index.

        Args:
            index: The index to get the NPC at

        Returns:
            The function to run the user flow for this NPC,
            or None otherwise.
        """
        if index >= len(self.adventures):
            return None
        else:
            return self.adventures[index][0].user_flow

    def create_adventure(self, npc: SceneNpc):
        """
        Adds an NPC to the Scene.

        Args:
            adventure: The NPC to represent the Adventure
        """
        # TODO: parse NPC to Adventure
        self.adventures.append((Adventure(), npc))

    def get_adventures(self) -> List[SceneNpc]:
        """
        Gets the list of NPCs in the SceneCoupler.

        Returns:
            The list of NPCs
        """
        return [adv[1] for adv in self.adventures]
