import abc
import json
import logging
from typing import Dict, List, Optional, Tuple

from config.logger import logger_config
from data.scene import Scene as SceneData
from data.scene import SceneNpc
from engine.convo import BaseConvoCoupler
from engine.models import Function, Message
from engine.openai_api import call_api_function


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
    def get_npcs(self) -> List[Tuple[SceneNpc, bool]]:
        """
        Gets the list of NPCs in the SceneCoupler.

        Returns:
            The list of NPCs and whether they are discovered
        """
        pass

    @abc.abstractclassmethod
    def get_npc_req(
        self, index: int
    ) -> Tuple[List[Message], Function, Dict[str, int]]:
        """
        Gets the function to determine if the user can discover the NPC.

        Args:
            index: The index of the NPC to get the function for

        Returns:
            The list of messages to give the API
            The function to give the API
            The dictionary of parameter name to index of NPCs
        """
        pass

    @abc.abstractclassmethod
    def discover_npc(self, index: int):
        """
        Discovers the NPC at the specified index.

        Args:
            index: The index of the NPC to discover
        """
        pass


class Scene:
    """The Scene class for holding NPCs"""

    logger: logging.Logger
    coupler: BaseSceneCoupler
    data: SceneData

    def __init__(self, coupler: BaseSceneCoupler, data: SceneData):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logger_config.level)

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

    def process_npc_discovery(self, index: int) -> List[int]:
        """
        Processes the NPC discovery.

        Args:
            index: The index of the current NPC

        Returns:
            The list of indices of NPCs discovered
        """
        messages, function, indices = self.coupler.get_npc_req(index)
        response = call_api_function(messages, function)

        # Parse the arguments
        if response.choices[0].message.function_call.name != function.name:
            self.logger.warning("Function is not called.")
            return []

        arguments = response.choices[0].message.function_call.arguments
        arguments = json.loads(arguments)

        self.logger.info(f"Arguments parsed: {arguments}")

        # Get the indices of the NPCs discovered
        indices_discovered = []
        for name, index in indices.items():
            if name in arguments and arguments[name]:
                self.coupler.discover_npc(index)
                indices_discovered.append(index)

        return indices_discovered
