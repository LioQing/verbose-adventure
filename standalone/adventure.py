import logging
import traceback

from config.adventure import adventure_config
from engine.convo import Convo
from engine.models import Message, Role

from .couplers.convo import ConvoCoupler


class Adventure:
    """The main adventure class"""

    logger: logging.Logger
    convo_coupler: ConvoCoupler
    convo: Convo

    def __init__(self, convo_coupler: ConvoCoupler):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(adventure_config.log_level)

        self.convo_coupler = convo_coupler
        self.convo = Convo(self.convo_coupler)

        self.logger.info("Adventure created")

    def run(self):
        """Start the adventure"""
        self.logger.info("Adventure started")

        self.init_adventure()

        while self.user_flow():
            pass

        self.logger.info("Adventure ended")
        print(f"Used {self.convo_coupler.token_used} tokens")

    def init_adventure(self):
        """Initialize the adventure"""
        self.logger.info("Initializing adventure")

        init_story = self.convo.init_story()
        self.print_assistant_response(init_story)

        self.logger.info("Adventure initialized")

    def user_flow(self) -> bool:
        """
        Do the user flow

        Returns:
            True if the conversation should continue, False otherwise
        """
        try:
            user_input = self.get_user_input()
            user_message = Message(role=Role.USER, content=user_input)
            user_response = self.convo.process_user_response(user_message)

            if user_response is None:
                print("Session ended")
                return False

            api_response = self.convo.process_api_response()

            summary = self.convo.summarize()
            if summary:
                self.print_summary_response(summary)

            self.print_assistant_response(api_response)
        except Exception as e:
            print(traceback.format_exc())
            print(f"Error: {e}")

        return True

    def get_user_input(self) -> str:
        """Get user input"""
        return input("> ")

    def print_assistant_response(self, message: Message):
        """Output the response of the assistant"""
        response = message.content
        print(f"Assistant: {response}")

    def print_summary_response(self, message: Message):
        """Output the response of the assistant"""
        response = message.content
        print(f"Summary: {response}")
