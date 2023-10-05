import abc
import logging
from typing import Callable, List, Optional

from config.adventure import adventure_config
from data.scene import SceneNpc


class BaseSceneCoupler(abc.ABC):
    """
    The abstract base class for SceneCoupler.

    Note that in Scene, NPC is an equivalent name for Adventure.
    """

    @abc.abstractclassmethod
    def get_adventure(self, index: int) -> Optional[Callable]:
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
    def create_adventure(self, npc: SceneNpc):
        """
        Adds an NPC to the Scene.

        Args:
            adventure: The NPC to represent the Adventure
        """
        pass

    @abc.abstractclassmethod
    def get_adventures(self) -> List[SceneNpc]:
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
    num_npcs: int

    def __init__(self, coupler: BaseSceneCoupler, num_npcs: int):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(adventure_config.log_level)

        self.coupler = coupler
        self.num_npcs = num_npcs

        self.logger.info("Scene created.")

    def init_scene(self):
        """Initializes a scene with the specified number of NPCs."""
        for i in range(self.num_npcs):
            # TODO: parse NPC data
            self.coupler.create_adventure(
                SceneNpc(name=f"NPC {i}", character="", knowledges=[])
            )

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

        if user_flow := self.coupler.get_adventure(index):
            user_flow()
        else:
            print("Invalid index.")

        return True
