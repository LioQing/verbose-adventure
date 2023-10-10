import abc
import logging
from typing import List, Optional

from config.adventure import adventure_config
from data.scene import Scene as SceneData
from data.scene import SceneNpc
from engine.convo import BaseConvoCoupler


class BaseSceneCoupler(abc.ABC):
    """
    The abstract base class for SceneCoupler.

    Note that in Scene, NPC is an equivalent name for Adventure.
    """

    @abc.abstractclassmethod
    def get_npc_user_flow(self, index: int) -> BaseConvoCoupler:
        """
        Gets the function to run the user flow at this index.

        Args:
            index: The index to get the NPC at

        Returns:
            The convo coupler of the NPC at this index,
        """
        pass

    @abc.abstractclassmethod
    def create_npc(self, scene: SceneData, npc: SceneNpc):
        """
        Adds an NPC to the Scene.

        Args:
            scene: The Scene to add the NPC to
            npc: The NPC to represent the Adventure
        """
        pass

    @abc.abstractclassmethod
    def get_npcs(self) -> List[SceneNpc]:
        """
        Gets the list of NPCs in the SceneCoupler.

        Returns:
            The list of NPCs
        """
        pass

    # TODO: Add get_npc_req

    # TODO: ADd discover_npc


class Scene:
    """The Scene class for holding NPCs"""

    logger: logging.Logger
    coupler: BaseSceneCoupler
    data: SceneData

    def __init__(self, coupler: BaseSceneCoupler, data: SceneData):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(adventure_config.log_level)

        self.coupler = coupler
        self.data = data

        self.logger.info(f"Scene {self.data.id} created.")

    def init_scene(self):
        """Initializes a scene with the specified number of NPCs."""
        for npc in self.data.npcs:
            self.coupler.create_npc(self.data, npc)

    def process_user_selection(self, index: int) -> Optional[BaseConvoCoupler]:
        """
        Processes the user selection.

        Args:
            index: The index of the NPC to talk to

        Returns:
            None if the user wants to exit, otherwise the NPC's convo coupler
        """
        if index == -1:
            print("Exiting per user request.")
            return None

        npc_coupler = self.coupler.get_npc_user_flow(index)
        return npc_coupler

    # TODO: Add process_npc_discovery
