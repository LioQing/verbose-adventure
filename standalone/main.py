import logging

from utils import formatter

from .scene_runner import SceneRunner

logging.basicConfig()
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(formatter.ColoredFormatter())
logger.handlers.clear()
logger.addHandler(handler)


def main():
    """Main entry point"""
    from data.scene.power_plant import scene as scene_data

    scene = SceneRunner(scene_data)
    scene.run()


if __name__ == "__main__":
    main()
