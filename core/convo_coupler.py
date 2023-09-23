from typing import List, Optional, Tuple

from engine import models as engine_models
from engine.convo import BaseConvoCoupler


class ConvoCoupler(BaseConvoCoupler):
    """Abstract class for Convo to communicate with its data state"""

    def get_init_message(self) -> engine_models.Message:
        """
        Get the initial message

        Returns:
            The initial message
        """
        pass

    def save_api_response(
        self, chatcmpl: engine_models.Chatcmpl
    ) -> engine_models.Message:
        """
        Save the API response

        Args:
            chatcmpl: The API response

        Returns:
            The chosen response message
        """
        pass

    def save_user_response(self, message: engine_models.Message):
        """
        Save the user response

        Args:
            message: The user message
        """
        pass

    def get_built_messages(
        self, history_length: int
    ) -> List[engine_models.Message]:
        """
        Build the message list for the OpenAI call

        Args:
            n: The number of messages to build from history

        Returns:
            The list of messages (system message, summary message, history)
        """
        pass

    def get_summary_messages(
        self, history_length: int
    ) -> Tuple[List[engine_models.Message], Optional[engine_models.Message]]:
        """
        Get the message history and previous summary for the summary

        Args:
            n: The number of messages to build from history

        Returns:
            The list of messages history
            Optional previous summary message
        """
        pass

    def save_summary_response(
        self, chatcmpl: engine_models.Chatcmpl
    ) -> engine_models.Message:
        """
        Save the summary message

        Args:
            chatcmpl: The API response

        Returns:
            The summary message
        """
        pass

    def should_stop(self, message: engine_models.Message) -> bool:
        """
        Return if the conversation should stop

        Args:
            message: The user message

        Returns:
            True if the conversation should stop, False otherwise
        """
        pass

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
        pass


convo_coupler = ConvoCoupler()
