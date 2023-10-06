import abc
import logging
from typing import Callable, List, Optional

from config.adventure import adventure_config
from data.scene import Scene as SceneData
from data.scene import SceneNpc


class BaseSceneCoupler(abc.ABC):
    """
    The abstract base class for SceneCoupler.

    Note that in Scene, NPC is an equivalent name for Adventure.
    """

    @abc.abstractclassmethod
    def get_npc_user_flow(self, index: int) -> Optional[Callable]:
        """
        Gets the function to run the user flow at this index if it exists.

        Args:
            index: The index to get the NPC at

        Returns:
            The function to run the user flow at this index,
            or None otherwise.
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

    def process_user_selection(self, index: int) -> bool:
        """
        Processes the user selection.

        Args:
            index: The index of the NPC to talk to

        Returns:
            True if the user requests exiting, False otherwise.
        """
        if index == -1:
            print("Exiting per user request.")
            return False

        if user_flow := self.coupler.get_npc_user_flow(index):
            user_flow()
        else:
            print("Invalid index.")

        return True
