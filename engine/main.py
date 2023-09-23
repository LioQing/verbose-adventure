import logging

from . import adventure

logging.basicConfig()


def main():
    """Main entry point"""
    adv = adventure.Adventure()
    adv.run()


if __name__ == "__main__":
    main()
