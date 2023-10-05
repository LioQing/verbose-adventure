import logging
from typing import Callable, List, Optional, Tuple

from config.adventure import adventure_config
from data.scene import Scene, SceneNpc
from engine.scene import BaseSceneCoupler

from ..adventure import Adventure
from .convo import SceneNpcConvoCoupler


class SceneCoupler(BaseSceneCoupler):
    """The concrete SceneCoupler implementation."""

    logger: logging.Logger
    npcs: List[Tuple[Adventure, SceneNpc]]

    @property
    def token_used(self) -> int:
        """Gets the number of tokens used for all NPC in the scene"""
        return sum(adv[0].convo_coupler.token_used for adv in self.npcs)

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(adventure_config.log_level)
        self.npcs = []

    def get_npc_user_flow(self, index: int) -> Optional[Callable]:
        """
        Gets the function of the NPC to run the user flow at this index.

        Args:
            index: The index to get the NPC at

        Returns:
            The function to run the user flow for this NPC,
            or None otherwise.
        """
        if index >= len(self.npcs):
            return None
        else:
            return self.npcs[index][0].user_flow

    def create_npc(self, scene: Scene, npc: SceneNpc):
        """
        Adds an NPC to the Scene.

        Args:
            scene: The Scene to add the NPC to
            npc: The NPC to represent the Adventure
        """
        adv = self.__parse_npc_to_adventure(scene, npc)
        self.npcs.append((adv, npc))

    def get_npcs(self) -> List[SceneNpc]:
        """
        Gets the list of NPCs in the SceneCoupler.

        Returns:
            The list of NPCs
        """
        return [adv[1] for adv in self.npcs]

    def __parse_npc_to_adventure(
        self, scene: Scene, npc: SceneNpc
    ) -> Adventure:
        """Parses an NPC to an Adventure"""
        return Adventure(
            convo_coupler=SceneNpcConvoCoupler(
                scene.system_message,
                npc,
            )
        )
