import logging
from typing import Dict, List, Optional, Tuple

from config.convo import convo_config
from config.logger import logger_config
from data.scene import Scene, SceneNpc
from engine.convo import BaseConvoCoupler
from engine.models import Function, Message, Parameter, Parameters
from engine.scene import BaseSceneCoupler

from ..adventure import Adventure
from .convo import ConvoCoupler, SceneNpcConvoCoupler


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
        self.logger.setLevel(logger_config.level)
        self.npcs = []

    def get_npc_user_flow(self, index: int) -> Optional[BaseConvoCoupler]:
        """
        Gets the function to run the user flow at this index if it exists.

        Args:
            index: The index to get the NPC at

        Returns:
            The convo coupler of the NPC at this index,
        """
        if index >= len(self.npcs):
            return None
        else:
            return self.npcs[index][0].convo_coupler

    def create_npc(self, scene: Scene, npc: SceneNpc):
        """
        Adds an NPC to the Scene.

        Args:
            scene: The Scene to add the NPC to
            npc: The NPC to represent the Adventure
        """
        adv = self.__parse_npc_to_adventure(scene, npc)
        self.npcs.append((adv, npc))

    def get_npcs(self) -> List[Tuple[SceneNpc, bool]]:
        """
        Gets the list of NPCs in the SceneCoupler.

        Returns:
            The list of NPCs and whether they are discovered
        """
        return [
            (npc, adv.convo_coupler.discovered) for (adv, npc) in self.npcs
        ]

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
        messages = ConvoCoupler.get_built_messages(
            self.npcs[index][0].convo_coupler,
            convo_config.history_length,
        )

        npc_indices = dict()
        parameters = dict()
        for i, (adv, npc) in enumerate(self.npcs):
            scene_convo_coupler: SceneNpcConvoCoupler = adv.convo_coupler
            if scene_convo_coupler.discovered:
                continue

            param_name = f"is_{npc.name.replace(' ', '_')}_discovered"
            npc_indices[param_name] = i
            parameters[param_name] = Parameter(
                description=(
                    f"Whether or not {npc.name} - {npc.title} is discovered"
                    f" given the discovery requirement of {npc.name}:"
                    f" {npc.discover_requirement}"
                ),
                type="boolean",
                required=True,
            )

        func = Function(
            name="discover_npc",
            description=(
                "Given the discovery requirement of each NPC and the"
                " conversation messages so far, determine if the user"
                " discovered any new NPC or not given."
            ),
            parameters=Parameters(
                parameters=parameters,
            ),
        )

        return messages, func, npc_indices

    def discover_npc(self, index: int):
        """
        Discovers the NPC at the specified index.

        Args:
            index: The index of the NPC to discover
        """
        scene_convo_coupler: SceneNpcConvoCoupler = self.npcs[index][
            0
        ].convo_coupler
        scene_convo_coupler.discovered = True

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
