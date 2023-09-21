import logging

from . import adventure
from .config import main_config

if main_config.enable_log:
    logging.basicConfig()


def main():
    """Main entry point"""
    adv = adventure.Adventure()
    adv.run()


if __name__ == "__main__":
    main()
