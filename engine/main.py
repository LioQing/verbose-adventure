import logging

from utils import formatter

from . import adventure

logging.basicConfig()
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(formatter.ColoredFormatter())
logger.handlers.clear()
logger.addHandler(handler)


def main():
    """Main entry point"""
    adv = adventure.Adventure()
    adv.run()


if __name__ == "__main__":
    main()
