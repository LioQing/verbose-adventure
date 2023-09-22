import logging

from config.main import main_config

from . import adventure

if main_config.enable_log:
    logging.basicConfig()


def main():
    """Main entry point"""
    adv = adventure.Adventure()
    adv.run()


if __name__ == "__main__":
    main()
