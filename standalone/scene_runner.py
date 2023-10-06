import logging
import traceback

from config.adventure import adventure_config
from data.scene import Scene as SceneData
from engine.scene import Scene

from .couplers.scene import SceneCoupler


class SceneRunner:
    """Class to run the scene"""

    logger: logging.Logger
    scene_coupler: SceneCoupler
    scene: Scene

    def __init__(self, scene_data: SceneData):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(adventure_config.log_level)

        self.scene_coupler = SceneCoupler()
        self.scene = Scene(self.scene_coupler, scene_data)

        self.logger.info("SceneRunner created.")

    def run(self):
        """Starts a run of this Scene."""
        self.logger.info("Scene started.")
        self.init_scene_runner()

        while self.user_flow():
            pass

        self.logger.info("Scene ended.")
        print(f"Used {self.scene_coupler.token_used} tokens")

    def init_scene_runner(self):
        """Initializes the SceneRunner."""
        self.logger.info("Initializing scene runner.")
        self.scene.init_scene()
        self.logger.info("Scene runner initialized.")

    def user_flow(self) -> bool:
        """
        Runs a round of user input.

        Returns:
            True if the user requests exiting, False otherwise.
        """
        print("Type the index of the NPC you want to talk to, or 0 to exit.")
        for i, npc in enumerate(self.scene_coupler.get_npcs()):
            print(f"{i + 1}. {npc.name:<10} - {npc.title}")
        print("0. Exit")
        user_input = self.get_user_input()

        try:
            index = int(user_input) - 1
            return self.scene.process_user_selection(index)
        except Exception as e:
            print(traceback.format_exc())
            print(f"Error: {e}")

        return True

    def get_user_input(self) -> str:
        """Get user input"""
        return input("Scene > ")
