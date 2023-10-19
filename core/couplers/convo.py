import json
import logging
from typing import List

from config.adventure import adventure_config
from config.convo import convo_config
from config.logger import logger_config
from engine import models as engine_models
from engine.convo import BaseConvoCoupler
from engine.openai_api import call_api_function

from .. import models


class ConvoCoupler(BaseConvoCoupler):
    """Abstract class for Convo to communicate with its data state"""

    logger: logging.Logger
    adventure: models.Adventure

    def __init__(self, adventure: models.Adventure):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logger_config.level)

        self.adventure = adventure

        self.logger.info("ConvoCoupler created")

    def get_init_message(self) -> engine_models.Message:
        """
        Get the initial message

        Returns:
            The initial message
        """
        self.logger.info("Getting init message")
        return engine_models.Message(
            role=engine_models.Role.SYSTEM,
            content=(
                f"{self.adventure.system_message} "
                f"{self.adventure.start_message}"
            ),
        )

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
        adventure = self.adventure
        summary = adventure.summary
        messages = models.Message.objects.get_latest_n_messages(
            adventure, convo_config.history_length
        )
        chatcmpl_model = models.Chatcmpl.objects.create_from_engine_chatcmpl(
            adventure,
            summary,
            messages,
            chatcmpl,
            is_summary=False,
            choice_index=adventure_config.default_choice_index,
        )

        chosen = chatcmpl_model.choice_set.get(
            index=adventure_config.default_choice_index
        )
        self.adventure.latest_message = chosen.message
        self.adventure.iteration += 1
        self.adventure.save()

        self.logger.info(f"API response saved: {chosen.message}")

        return chatcmpl.choices[adventure_config.default_choice_index].message

    def save_user_response(self, message: engine_models.Message):
        """
        Save the user response

        Args:
            message: The user message
        """
        message_model = models.Message.objects.create_from_engine_message(
            self.adventure, message
        )
        self.adventure.latest_message = message_model
        self.adventure.iteration += 1
        self.adventure.save()

        self.logger.info(f"User response saved: {message}")

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
        self.logger.info("Building message list for OpenAI call")

        messages = []

        messages.append(
            engine_models.Message(
                role=engine_models.Role.SYSTEM,
                content=(
                    f"{self.adventure.system_message} "
                    + (
                        self.adventure.summary.summary
                        if self.adventure.summary
                        else ""
                    )
                ),
            )
        )

        messages.extend(
            [
                m.to_engine_message()
                for m in models.Message.objects.get_latest_n_messages(
                    self.adventure, history_length
                )
            ]
        )

        return messages

    def get_summary_messages(
        self, history_length: int
    ) -> List[engine_models.Message]:
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

        if self.adventure.summary is None:
            messages.append(
                engine_models.Message(
                    role=engine_models.Role.SYSTEM,
                    content=adventure_config.summary_system_message_no_prev,
                )
            )
        else:
            messages.append(
                engine_models.Message(
                    role=engine_models.Role.SYSTEM,
                    content=adventure_config.summary_system_message,
                )
            )
            messages.append(
                engine_models.Message(
                    role=engine_models.Role.ASSISTANT,
                    content=(
                        "The previous summary is:"
                        f" {self.adventure.summary.summary}"
                    ),
                )
            )

        json_history_messages = [
            m.to_engine_message()
            for m in models.Message.objects.get_latest_n_messages(
                self.adventure, history_length
            )
        ]
        messages.append(
            engine_models.Message(
                role=engine_models.Role.ASSISTANT,
                content=(
                    f"The conversation messages are: {json_history_messages}"
                ),
            )
        )

        return messages

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
        adventure = self.adventure
        summary = adventure.summary
        messages = models.Message.objects.get_latest_n_messages(
            adventure, convo_config.history_length
        )
        chatcmpl_model = models.Chatcmpl.objects.create_from_engine_chatcmpl(
            adventure,
            summary,
            messages,
            chatcmpl,
            is_summary=True,
            choice_index=adventure_config.default_choice_index,
        )

        chosen = chatcmpl_model.choice_set.get(
            index=adventure_config.default_choice_index
        )

        # Save summary
        new_summary = models.Summary.objects.create_from_engine_summary(
            adventure,
            chatcmpl.choices[adventure_config.default_choice_index].message,
        )
        adventure.summary = new_summary
        adventure.save()

        self.logger.info(f"Summary response saved: {chosen.message}")

        return chatcmpl.choices[adventure_config.default_choice_index].message

    def should_stop(self, message: engine_models.Message) -> bool:
        """
        Return if the conversation should stop

        Args:
            message: The user message

        Returns:
            True if the conversation should stop, False otherwise
        """
        return False

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
        return self.adventure.iteration % summary_interval in [0, 1]


class SceneNpcConvoCoupler(ConvoCoupler):
    """ConvoCoupler for Scene NPC"""

    logger: logging.Logger
    scene_system_message: str
    npc_adv_pair: models.SceneNpcAdventurePair

    def __init__(
        self, system_message: str, npc_adv_pair: models.SceneNpcAdventurePair
    ):
        adv = npc_adv_pair.adventure
        adv.system_message = f"{system_message} {npc_adv_pair.npc.character}"
        adv.start_message = ""
        adv.save()

        super().__init__(adv)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logger_config.level)

        self.scene_system_message = system_message
        self.npc_adv_pair = npc_adv_pair

        self.logger.info(
            f"SceneNpcConvoCoupler for {npc_adv_pair.npc.id} created"
        )

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
        messages = super().get_built_messages(history_length)

        self.logger.info("Adjusting system message list for OpenAI call")

        extra_knowledge = self.get_knowledge(messages)
        messages[0].content += f" {extra_knowledge}"

        return messages

    def get_knowledge(
        self, convo_messages: List[engine_models.Message]
    ) -> str:
        """
        Get the knowledge to use for the NPC

        Args:
            messages: The messages

        Returns:
            The knowledge to use
        """
        self.logger.info("Getting knowledge to use")

        # Prepare the function and messages
        function = engine_models.Function(
            name="get_knowledge",
            description=(
                "Get the assistant's knowledge to use for responding the"
                " user's message. The assistant and user refer to the"
                " conversation messages in the JSON list."
            ),
            parameters=engine_models.Parameters(
                parameters={
                    k.name: engine_models.Parameter(
                        type="boolean",
                        description=k.description,
                        required=True,
                    )
                    for k in self.npc_adv_pair.npc.knowledges.all()
                }
            ),
        )

        messages = []

        messages.append(
            engine_models.Message(
                role=engine_models.Role.SYSTEM,
                content=adventure_config.knowledge_system_message,
            )
        )

        json_convo_messages = [m.model_dump() for m in convo_messages]

        messages.append(
            engine_models.Message(
                role=engine_models.Role.USER,
                content=(
                    "The JSON list of conversation messages is:"
                    f" {json_convo_messages}"
                ),
            )
        )

        response = call_api_function(messages, function)

        self.npc_adv_pair.knowledge_selection_token_count += (
            response.usage.total_tokens
        )

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
            for k in self.npc_adv_pair.npc.knowledges.all()
            if arguments[k.name]
        )
