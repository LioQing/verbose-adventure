import abc
import logging
from typing import List, Optional

import openai

from config.convo import convo_config
from config.openai import open_ai_config

from .models import Chatcmpl, ChatcmplRequest, Message

openai.api_key = open_ai_config.key
openai.api_base = open_ai_config.url
openai.api_type = open_ai_config.api_type
openai.api_version = open_ai_config.version


class BaseConvoCoupler(abc.ABC):
    """Abstract class for Convo to communicate with its data state"""

    @abc.abstractclassmethod
    def get_init_message(self) -> Message:
        """
        Get the initial message

        Returns:
            The initial message
        """
        pass

    @abc.abstractclassmethod
    def save_api_response(self, chatcmpl: Chatcmpl) -> Message:
        """
        Save the API response

        Args:
            chatcmpl: The API response

        Returns:
            The chosen response message
        """
        pass

    @abc.abstractclassmethod
    def save_user_response(self, message: Message):
        """
        Save the user response

        Args:
            message: The user message
        """
        pass

    @abc.abstractclassmethod
    def get_built_messages(self, history_length: int) -> List[Message]:
        """
        Build the message list for the OpenAI call

        Args:
            n: The number of messages to build from history

        Returns:
            The list of messages (system message, summary message, history)
        """
        pass

    @abc.abstractclassmethod
    def get_summary_messages(self, history_length: int) -> List[Message]:
        """
        Get the message history and previous summary for the summary

        Args:
            n: The number of messages to build from history

        Returns:
            The list of messages (summary system message, summary message,
            history in JSON format)
        """
        pass

    @abc.abstractclassmethod
    def save_summary_response(self, chatcmpl: Chatcmpl) -> Message:
        """
        Save the summary message

        Args:
            chatcmpl: The API response

        Returns:
            The summary message
        """
        pass

    @abc.abstractclassmethod
    def should_stop(self, message: Message) -> bool:
        """
        Return if the conversation should stop

        Args:
            message: The user message

        Returns:
            True if the conversation should stop, False otherwise
        """
        pass

    @abc.abstractclassmethod
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


class Convo:
    """Conversation class for OpenAI API"""

    logger: logging.Logger
    coupler: BaseConvoCoupler

    def __init__(self, coupler: BaseConvoCoupler):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(convo_config.log_level)

        self.coupler = coupler

        self.logger.info("Convo created")

    def init_story(self) -> Message:
        """
        Initialize the story

        Returns:
            The chosen response message
        """
        self.logger.info("Initializing story")

        init_message = self.coupler.get_init_message()
        self.logger.info(f"Init message: {init_message}")

        chatcmpl = self._call_api([init_message])
        chosen = self.coupler.save_api_response(chatcmpl)

        self.logger.info("Story initialized")
        return chosen

    def process_user_response(self, message: Message) -> Optional[Message]:
        """
        Do the user response

        Args:
            message: The user message

        Returns:
            The user message if the conversation should continue,
            None otherwise
        """
        self.logger.info(f"Doing user response {message}")

        if self.coupler.should_stop(message):
            self.logger.info("Conversation should stop")
            return None

        self.coupler.save_user_response(message)

        self.logger.info("User response done, conversation should continue")
        return message

    def process_api_response(self) -> Message:
        """Do the API response."""
        self.logger.info("Doing API response")

        messages = self.coupler.get_built_messages(convo_config.history_length)

        chatcmpl = self._call_api(messages)
        chosen = self.coupler.save_api_response(chatcmpl)

        self.logger.info("API response done")
        return chosen

    def summarize(self) -> Optional[Message]:
        """
        Summarize the conversation

        Returns:
            The summary message if the conversation should be summarized,
            None otherwise
        """
        self.logger.info("Summarizing conversation")

        if not self.coupler.should_summarize(
            convo_config.history_length, convo_config.summary_interval
        ):
            self.logger.info("Conversation should not be summarized")
            return None

        # Summary messages
        messages = self.coupler.get_summary_messages(
            convo_config.history_length
        )

        # Call API
        chatcmpl = self._call_api(messages)
        summary_message = self.coupler.save_summary_response(chatcmpl)

        self.logger.info("Conversation summarized")
        return summary_message

    def _call_api(self, messages: List[Message]) -> Chatcmpl:
        """Call the OpenAI API with the given messages"""
        request = ChatcmplRequest(
            deployment_id=convo_config.deployment,
            model=convo_config.model,
            messages=[m.model_dump() for m in messages],
        )

        self.logger.debug(f"Calling API with request: {request}")

        response = openai.ChatCompletion.create(**request.model_dump())
        response = Chatcmpl(**response)

        self.logger.debug(f"API response: {response}")
        return response
