import abc
import logging
from enum import StrEnum
from typing import Any, Dict, List, Optional

import openai
from pydantic import BaseModel, Field

from config.convo import convo_config
from config.openai import open_ai_config

openai.api_key = open_ai_config.key
openai.api_base = open_ai_config.url
openai.api_type = open_ai_config.api_type
openai.api_version = open_ai_config.version


class Role(StrEnum):
    """Role enumeration for conversation messages"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class Message(BaseModel):
    """Message for conversation"""

    role: Role
    content: str
    name: Optional[str] = Field(None)

    def model_dump(self) -> Dict[str, Any]:
        """Dump the model"""
        dump = super().model_dump()
        if self.name is None:
            dump.pop("name")

        return dump


class ConvoStateCoupler(abc.ABC):
    """Abstract class for Convo to communicate with its data state"""

    @abc.abstractclassmethod
    def get_system_message(self) -> Optional[str]:
        """Get the system message"""
        pass

    @abs.abstractclassmethod
    def set_system_message(self, message: str):
        """Set the system message"""
        pass

    @abc.abstractclassmethod
    def get_summary_message(self) -> Optional[str]:
        """Get the summary message"""
        pass

    @abs.abstractclassmethod
    def set_summary_message(self, message: str):
        """Set the summary message"""
        pass

    @abc.abstractclassmethod
    def append_message(self, message: Message):
        """Append a message to the conversation"""
        pass

    @abc.abstractclassmethod
    def get_story_messages(self, num: int) -> List[Message]:
        """Get the last `num` messages in the current story"""
        pass

    @abc.abstractclassmethod
    def get_story_length(self) -> int:
        """Get the length of the message in the current story"""
        pass


class Convo:
    """Conversation class for OpenAI API"""

    logger: logging.Logger
    system_message: str
    summary_message: Optional[str]
    messages: List[Message]
    token_used: int

    def __init__(self, system_message: str):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(convo_config.log_level)

        self.system_message = system_message
        self.summary_message = None
        self.messages = []
        self.token_used = 0

        self.logger.info("Convo created")

    def add_message(self, message: Message):
        """Add a message to the conversation"""
        self.logger.info(f"Adding message {message}")
        self.messages.append(message)
        self._log_message(message)

    def set_summary_message(self, message: str):
        """Set the summary message"""
        self.logger.info(f"Setting summary message {message}")
        self.summary_message = message

    def get_response(self, user_message: str) -> str:
        """Call and get the response from the OpenAI API"""
        self.messages.append(Message(role=Role.USER, content=user_message))

        messages = self._build_messages()

        response = self._call_api(messages)
        response_message: str = response.choices[0].message.content

        # Summarize if needed
        if convo_config.summary_interval > 0:
            if len(self.messages) % convo_config.summary_interval == 0:
                self.set_summary_message(self.summarize())

        self.messages.append(
            Message(
                role=Role.ASSISTANT,
                content=response_message,
            )
        )
        self._log_response(response)

        # Summarize if needed
        if convo_config.summary_interval > 0:
            if len(self.messages) % convo_config.summary_interval == 0:
                self.set_summary_message(self.summarize())

        return response_message

    def summarize(self) -> str:
        """Summarize the text"""
        # Add message history
        message_history = convo_config.message_history
        history = self.messages[-message_history:]

        if self.summary_message:
            history.insert(
                0, Message(role=Role.SYSTEM, content=self.summary_message)
            )

        history_messages = repr([m.model_dump() for m in history])

        # Add summary system message
        summary_system_message = None
        if self.summary_message:
            summary_system_message = convo_config.summary_system_message
        else:
            summary_system_message = (
                convo_config.summary_system_message_no_prev
            )

        # Build message payload
        messages = [
            Message(
                role=Role.SYSTEM,
                content=summary_system_message,
            ),
            Message(role=Role.USER, content=history_messages),
        ]

        self._log_message(messages[0])

        response = self._call_api([m.model_dump() for m in messages])
        response_message: str = response.choices[0].message.content

        self._log_response(response)

        return response_message

    def _call_api(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Call the OpenAI API with the given messages"""
        self.logger.info(f"Calling API with messages: {messages}")

        response = openai.ChatCompletion.create(
            deployment_id=convo_config.deployment,
            model=convo_config.model,
            messages=messages,
        )

        self.token_used += response.usage.total_tokens

        self.logger.info(f"API response: {response}")

        return response

    def _log_response(self, response: dict):
        """Log the response"""
        self.logger.info(f"Logging response {response}")
        with open(convo_config.log_file, "a") as f:
            f.write(f"{response}\n")

    def _log_message(self, message: Message):
        """Log the message"""
        self.logger.info(f"Logging message {message}")
        with open(convo_config.log_file, "a") as f:
            f.write(f"{message}\n")

    def _build_messages(self) -> List[Dict[str, str]]:
        """Build the messages list for the OpenAI call"""
        messages: List[Message] = []

        # Add system message
        messages.append(
            Message(
                role=Role.SYSTEM,
                content=self.system_message,
            )
        )

        # Add summary message
        if self.summary_message:
            messages.append(
                Message(
                    role=Role.ASSISTANT,
                    content="A summary of previous story: "
                    + self.summary_message,
                )
            )

        # Add message history
        convo_config.message_history

        messages.extend(self.messages[-convo_config.message_history :])

        return [m.model_dump() for m in messages]
