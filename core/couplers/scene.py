import logging
from typing import List, Optional

import data.scene
from config.adventure import adventure_config
from core import models
from core.couplers.convo import SceneNpcConvoCoupler
from engine.scene import BaseConvoCoupler, BaseSceneCoupler


class SceneCoupler(BaseSceneCoupler):
    """The concrete SceneCoupler implementation."""

    logger: logging.Logger
    scene_runner: models.SceneRunner

    def __init__(self, scene_runner: models.SceneRunner):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(adventure_config.log_level)

        self.scene_runner = scene_runner

        self.logger.info("SceneCoupler created")

    def get_npc_user_flow(self, index: int) -> Optional[BaseConvoCoupler]:
        """
        Gets the function to run the user flow at this index if it exists.

        Args:
            index: The index to get the NPC at

        Returns:
            The convo coupler of the NPC at this index,
        """
        self.logger.info(f"Getting NPC user flow at {index}")

        npc_adv_pair: Optional[
            models.SceneNpcAdventurePair
        ] = self.scene_runner.scenenpcadventurepair_set.filter(
            npc__index=index
        ).first()

        if npc_adv_pair is None:
            return None

        return SceneNpcConvoCoupler(
            self.scene_runner.scene.system_message, npc_adv_pair
        )

    def create_npc(self, scene: data.scene.Scene, npc: data.scene.SceneNpc):
        """
        Adds an NPC to the Scene.

        Args:
            scene: The Scene to add the NPC to
            npc: The NPC to represent the Adventure
        """
        self.logger.info(f"Creating NPC {npc.id} in scene {scene.id}")

        adventure: models.Adventure = models.Adventure.objects.create(
            user=self.scene_runner.user,
            system_message=scene.system_message,
            start_message="",
        )

        npc: models.SceneNpc = models.SceneNpc.objects.get(id=npc.id)

        models.SceneNpcAdventurePair.objects.create(
            runner=self.scene_runner,
            npc=npc,
            adventure=adventure,
        )

    def get_npcs(self) -> List[data.scene.SceneNpc]:
        """
        Gets the list of NPCs in the SceneCoupler.

        Returns:
            The list of NPCs
        """
        self.logger.info("Getting NPCs")

        npc_adv_pair_set = self.scene_runner.scenenpcadventurepair_set.all()
        return [
            npc_adv_pair.npc.to_scene_data_npc()
            for npc_adv_pair in npc_adv_pair_set
        ]
