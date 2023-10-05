import abc
import logging
import traceback
from typing import List, Optional

from config.adventure import adventure_config
from engine.adventure import Adventure


class BaseSceneCoupler(abc.ABC):
    """The abstract base class for SceneCoupler."""

    @abc.abstractclassmethod
    def get_adventure(self, index: int) -> Optional[Adventure]:
        """
        Gets the Adventure instance at this index, if it exists.

        Args:
            index: The index to get an Adventure at

        Returns:
            The Adventure at this index, or an empty Optional otherwise.
        """
        pass

    @abc.abstractclassmethod
    def add_adventure(self, adventure: Adventure):
        """
        Adds a Adventure to the Scene.

        Args:
            adventure: The Adventure to Add
        """
        pass

    @abc.abstractclassmethod
    def get_adventures(self) -> List[Adventure]:
        """
        Gets the list of adventures in the SceneCoupler.

        Returns:
            The list of Adventures
        """
        pass


class SceneCoupler(BaseSceneCoupler):
    """The concrete SceneCoupler implementation."""

    logger: logging.Logger
    adventures: List[Adventure]

    def __init__(self, adventures: List[Adventure] = []):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(adventure_config.log_level)
        self.adventures = adventures

    def get_adventure(self, index: int) -> Optional[Adventure]:
        """
        Gets the Adventure instance at this index, if it exists.

        Args:
            index: The index to get an Adventure at

        Returns:
            The Adventure at this index, or an empty Optional otherwise.
        """
        if index >= len(self.adventures):
            return None
        else:
            return self.adventures[index]

    def get_adventures(self) -> List[Adventure]:
        """
        Gets the list of adventures in the SceneCoupler.

        Returns:
            The list of Adventures
        """
        return self.adventures

    def add_adventure(self, adv: Adventure):
        """
        Adds a Adventure to the Scene.

        Args:
            adventure: The Adventure to Add
        """
        self.adventures.append(adv)


class Scene:
    """The Scene class for holding Adventures"""

    logger: logging.Logger
    scene_coupler: SceneCoupler
    num_npcs: int

    def __init__(self, num_npcs: int):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(adventure_config.log_level)
        self.scene_coupler = SceneCoupler()
        self.num_npcs = num_npcs

        self.logger.info("Scene created.")

    def init_scene(self):
        """Initializes a scene with the specified number of NPCs."""
        for _ in range(self.num_npcs):
            adv = Adventure()
            self.scene_coupler.add_adventure(adv)

    def run(self):
        """Starts a run of this Scene."""
        self.logger.info("Scene started.")
        self.init_scene()

        while self.user_flow():
            pass

        self.logger.info("Scene ended.")
        tokens_used = sum(
            adv.convo_coupler.token_used
            for adv in self.scene_coupler.get_adventures()
        )
        print(f"Used {tokens_used} tokens.")

    def user_flow(self) -> bool:
        """
        Runs a round of user input.

        Returns:
            True if the user requests exiting, False otherwise.
        """
        for count, advs in enumerate(self.scene_coupler.get_adventures()):
            print(f"Adventure {count + 1} ")
        user_input = self.get_user_input()
        try:
            index = int(user_input) - 1
            if index == -1:
                print("Exiting per user request.")
                return False

            optional_adv = self.scene_coupler.get_adventure(index)
            if optional_adv is None:
                print("No such adventure!")
                return True
            optional_adv.user_flow()
        except Exception as e:
            print(traceback.format_exc())
            print(f"Error: {e}")

        return True

    def get_user_input(self) -> str:
        """Get user input"""
        return input("Scene > ")
