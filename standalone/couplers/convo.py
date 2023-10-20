import json
import logging
from typing import List, Optional

from config.adventure import adventure_config
from config.logger import logger_config
from data.scene import SceneNpc
from engine.convo import BaseConvoCoupler
from engine.models import (
    Chatcmpl,
    Function,
    Message,
    Parameter,
    Parameters,
    Role,
)
from engine.openai_api import call_api_function


class ConvoCoupler(BaseConvoCoupler):
    """Coupler for Adventure Convo"""

    logger: logging.Logger
    message: List[Message]
    chatcmpl: List[Chatcmpl]
    summary: Optional[str]

    system_message: str
    start_message: str
    summary_system_message: str
    summary_system_message_no_prev: str

    def __init__(
        self,
        system_message: Optional[str] = None,
        start_message: Optional[str] = None,
        summary_system_message: Optional[str] = None,
        summary_system_message_no_prev: Optional[str] = None,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logger_config.level)

        self.message = []
        self.chatcmpl = []
        self.summary = None

        self.system_message = system_message or adventure_config.system_message
        self.start_message = start_message or adventure_config.start_message
        self.summary_system_message = (
            summary_system_message or adventure_config.summary_system_message
        )
        self.summary_system_message_no_prev = (
            summary_system_message_no_prev
            or adventure_config.summary_system_message_no_prev
        )

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
            content=f"{self.system_message} {self.start_message}",
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
        chosen = chatcmpl.choices[
            adventure_config.default_choice_index
        ].message
        self.message.append(chosen)
        self.logger.debug(f"API response saved: {chosen}")

        return chosen

    def save_user_response(self, message: Message):
        """
        Save the user response

        Args:
            message: The user message
        """
        self.message.append(message)
        self.logger.debug(f"User response saved: {message}")

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
                content=self.system_message
                + (f" {self.summary}" if self.summary else ""),
            )
        )

        messages.extend(self.message[-history_length:])

        return messages

    def get_summary_messages(self, history_length: int) -> List[Message]:
        """
        Get the message history and previous summary for the summary

        Args:
            n: The number of messages to build from history

        Returns:
            The list of messages (summary system message, summary message,
            history in JSON format)
        """
        self.logger.info("Getting messages for summary")

        messages = []

        if self.summary is not None:
            messages.append(
                Message(
                    role=Role.SYSTEM,
                    content=self.summary_system_message_no_prev,
                )
            )
        else:
            messages.append(
                Message(
                    role=Role.SYSTEM,
                    content=self.summary_system_message,
                )
            )
            messages.append(
                Message(
                    role=Role.ASSISTANT,
                    content=f"The previous summary is: {self.summary}",
                )
            )

        json_history_messages = [
            m.model_dump() for m in self.message[-history_length:]
        ]
        messages.append(
            Message(
                role=Role.ASSISTANT,
                content=(
                    f"The conversation messages are: {json_history_messages}"
                ),
            )
        )

        return messages

    def save_summary_response(self, chatcmpl: Chatcmpl) -> Message:
        """
        Save the summary message

        Args:
            chatcmpl: The API response

        Returns:
            The summary message
        """
        self.chatcmpl.append(chatcmpl)
        chosen = chatcmpl.choices[
            adventure_config.default_choice_index
        ].message
        self.summary = chosen.content
        self.logger.debug(f"Summary response saved: {self.summary}")

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
        return len(self.message) % summary_interval in [0, 1]


class SceneNpcConvoCoupler(ConvoCoupler):
    """
    ConvoCoupler for Scene NPC

    It manages the knowledge and adjust the system message accordingly.
    """

    logger: logging.Logger
    scene_system_message: str
    npc: SceneNpc
    discovered: bool
    knowledge_selection_token_used: int

    def __init__(self, system_message: str, npc: SceneNpc):
        super().__init__(
            system_message=f"{system_message} {npc.character}",
            start_message="",
        )

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logger_config.level)

        self.scene_system_message = system_message
        self.npc = npc
        self.discovered = False
        self.knowledge_selection_token_used = 0

        if self.npc.discover_requirement is None:
            self.discovered = True

        self.logger.info(f"SceneNpcConvoCoupler for {npc.id} created")

    @property
    def token_used(self) -> int:
        """
        Get the number of tokens used

        Returns:
            The number of tokens used
        """
        return super().token_used + self.knowledge_selection_token_used

    def get_built_messages(self, history_length: int) -> List[Message]:
        """
        Build the message list for the OpenAI call

        Args:
            n: The number of messages to build from history

        Returns:
            The list of messages (system message, summary message, history)
        """
        messages = super().get_built_messages(history_length)

        self.logger.info("Adjusting system message list for OpenAI call")

        extra_knowledge = self.get_knowledge(messages)
        messages[0].content += f" {extra_knowledge}"

        return messages

    def should_stop(self, message: Message) -> bool:
        """
        Return if the conversation should stop

        Args:
            message: The user message

        Returns:
            True if the conversation should stop, False otherwise
        """
        return message.content == "back"

    def get_knowledge(self, convo_messages: List[Message]) -> str:
        """
        Get the knowledge to use for the NPC

        Args:
            messages: The messages

        Returns:
            The knowledge to use
        """
        self.logger.info("Getting knowledge to use")

        # Prepare the function and messages
        function = Function(
            name="get_knowledge",
            description=(
                "Get the assistant's knowledge to use for responding the"
                " user's message. The assistant and user refer to the"
                " conversation messages in the JSON list. True if the"
                " knowledge is needed, False otherwise."
            ),
            parameters=Parameters(
                parameters={
                    k.name: Parameter(
                        type="boolean",
                        description=k.description,
                        required=True,
                    )
                    for k in self.npc.knowledges
                }
            ),
        )

        messages = []

        messages.append(
            Message(
                role=Role.SYSTEM,
                content=adventure_config.knowledge_system_message,
            )
        )

        json_convo_messages = [m.model_dump() for m in convo_messages]

        messages.append(
            Message(
                role=Role.USER,
                content=(
                    "The JSON list of conversation messages is:"
                    f" {json_convo_messages}"
                ),
            )
        )

        response = call_api_function(messages, function)

        self.knowledge_selection_token_used += response.usage.total_tokens

        # Parse the arguments
        if response.choices[0].message.function_call.name != function.name:
            self.logger.warning("Function is not called.")
            return ""

        arguments = response.choices[0].message.function_call.arguments
        arguments = json.loads(arguments)

        self.logger.info(f"Arguments parsed: {arguments}")

        # Get the knowledge
        return " ".join(
            k.knowledge
            for k in self.npc.knowledges
            if k.name in arguments and arguments[k.name]
        )
