import logging
import traceback
from typing import List, Optional, Tuple

from config.adventure import adventure_config

from .convo import BaseConvoCoupler, Chatcmpl, Convo, Message, Role


class ConvoCoupler(BaseConvoCoupler):
    """Coupler for Adventure Convo"""

    logger: logging.Logger
    message: List[Message]
    chatcmpl: List[Chatcmpl]
    summary: Optional[str]

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(adventure_config.log_level)

        self.message = []
        self.chatcmpl = []
        self.summary = None

        self.logger.info("ConvoCoupler created")

    @property
    def token_used(self) -> int:
        """
        Get the number of tokens used

        Returns:
            The number of tokens used
        """
        return sum(c.usage.total_tokens for c in self.chatcmpl)

    def get_init_message(self) -> Message:
        """
        Get the initial message

        Returns:
            The initial message
        """
        self.logger.info("Getting init message")
        return Message(
            role=Role.SYSTEM,
            content=(
                f"{adventure_config.system_message} "
                f"{adventure_config.start_message}"
            ),
        )

    def save_api_response(self, chatcmpl: Chatcmpl) -> Message:
        """
        Save the API response

        Args:
            chatcmpl: The API response

        Returns:
            The chosen response message
        """
        self.chatcmpl.append(chatcmpl)
        chosen = chatcmpl.choices[0].message
        self.message.append(chosen)
        self.logger.info(f"API response saved: {chosen}")

        return chosen

    def save_user_response(self, message: Message):
        """
        Save the user response

        Args:
            message: The user message
        """
        self.message.append(message)
        self.logger.info(f"User response saved: {message}")

    def get_built_messages(self, history_length: int) -> List[Message]:
        """
        Build the message list for the OpenAI call

        Args:
            n: The number of messages to build from history

        Returns:
            The list of messages (system message, summary message, history)
        """
        self.logger.info("Building message list for OpenAI call")

        messages = []

        messages.append(
            Message(
                role=Role.SYSTEM,
                content=adventure_config.system_message
                + (f" {self.summary}" if self.summary else ""),
            )
        )

        messages.extend(self.message[-history_length:])

        return messages

    def get_summary_messages(
        self, history_length: int
    ) -> Tuple[List[Message], Optional[str]]:
        """
        Get the message history and previous summary for the summary

        Args:
            n: The number of messages to build from history

        Returns:
            The list of messages history
            Optional previous summary
        """
        self.logger.info(
            "Getting message history and previous summary for summary"
        )

        if self.summary is None:
            return self.message[-history_length:], None

        return (
            self.message[-history_length:],
            Message(role=Role.ASSISTANT, content=self.summary),
        )

    def save_summary_response(self, chatcmpl: Chatcmpl) -> Message:
        """
        Save the summary message

        Args:
            chatcmpl: The API response

        Returns:
            The summary message
        """
        self.chatcmpl.append(chatcmpl)
        chosen = chatcmpl.choices[0].message
        self.summary = chosen.content
        self.logger.info(f"Summary response saved: {self.summary}")

        return chosen

    def should_stop(self, message: Message) -> bool:
        """
        Return if the conversation should stop

        Args:
            message: The user message

        Returns:
            True if the conversation should stop, False otherwise
        """
        return message.content == "exit()"

    def should_summarize(
        self, history_length: int, summary_interval: int
    ) -> bool:
        """
        Return if the conversation should be summarized

        Args:
            history_length: The length of the message history
            summary_interval: The interval to summarize

        Returns:
            True if the conversation should be summarized, False otherwise
        """
        return len(self.message) % summary_interval == 0


class Adventure:
    """The main adventure class"""

    logger: logging.Logger
    convo_coupler: ConvoCoupler
    convo: Convo

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(adventure_config.log_level)

        self.convo_coupler = ConvoCoupler()
        self.convo = Convo(self.convo_coupler)

        self.logger.info("Adventure created")

    def run(self):
        """Start the adventure"""
        self.logger.info("Adventure started")

        init_story = self.convo.init_story()
        self.print_assistant_response(init_story)

        while True:
            try:
                user_input = self.get_user_input()
                user_message = Message(role=Role.USER, content=user_input)
                user_response = self.convo.process_user_response(user_message)

                if user_response is None:
                    print("Session ended")
                    break

                api_response = self.convo.process_api_response()

                summary = self.convo.summarize()
                if summary:
                    self.print_summary_response(summary)

                self.print_assistant_response(api_response)
            except Exception as e:
                print(traceback.format_exc())
                print(f"Error: {e}")

        self.logger.info("Adventure ended")
        print(f"Used {self.convo_coupler.token_used} tokens")

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
