import logging

from utils import formatter

from . import scene  # , adventure

logging.basicConfig()
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(formatter.ColoredFormatter())
logger.handlers.clear()
logger.addHandler(handler)


def main():
    """Main entry point"""
    """adv = adventure.Adventure(
        system_message=(
            "You are an assistant to help the user with any information they"
            " need."
        ),
        start_message="You start by greeting the user.",
    )
    adv.run()
    """
    sc = scene.Scene(5)
    sc.run()


if __name__ == "__main__":
    main()
