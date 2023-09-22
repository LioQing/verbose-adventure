import logging

from config.adventure import adventure_config

from .convo import Convo, ConvoStateCoupler


class AdventureConvoStateCoupler(ConvoStateCoupler):
    """Coupler for Adventure Convo"""


class Adventure:
    """The main adventure class"""

    logger: logging.Logger
    convo: Convo
    system_message: str

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(adventure_config.log_level)

        self.convo = Convo()
        self.system_message = adventure_config.system_message

        self.logger.info("Adventure created")

    def run(self):
        """Start the adventure"""
        self.logger.info("Adventure started")

        print("Say something to start the game")
        while True:
            try:
                user_input = self.get_user_input()

                if user_input == "exit":
                    print(
                        "Conversation ended, token used:"
                        f" {self.convo.token_used}"
                    )
                    break
                elif user_input == "summarize()":
                    summerization = self.convo.summarize()
                    print(f"Summarization: {summerization}")
                    continue

                response = self.convo.get_response(
                    user_input, self.system_message
                )
                print(f"Assistant: {response}")
            except Exception as e:
                print(f"Error: {e}")

    def get_user_input(self) -> str:
        """Get user input"""
        return input("> ")
