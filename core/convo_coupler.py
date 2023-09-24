import logging
from typing import List, Optional, Tuple

from config.adventure import adventure_config
from config.convo import convo_config
from engine import models as engine_models
from engine.convo import BaseConvoCoupler

from . import models


class ConvoCoupler(BaseConvoCoupler):
    """Abstract class for Convo to communicate with its data state"""

    adventure: models.Adventure

    def __init__(self, adventure: models.Adventure):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(adventure_config.log_level)

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
    ) -> Tuple[List[engine_models.Message], Optional[engine_models.Message]]:
        """
        Get the message history and previous summary for the summary

        Args:
            n: The number of messages to build from history

        Returns:
            The list of messages history
            Optional previous summary message
        """
        self.logger.info(
            "Getting message history and previous summary for summary"
        )

        history = [
            m.to_engine_message()
            for m in models.Message.objects.get_latest_n_messages(
                self.adventure, history_length
            )
        ]

        if self.adventure.summary is None:
            return history, None

        return history, engine_models.Message(
            role=engine_models.Role.ASSISTANT,
            content=self.adventure.summary.summary,
        )

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
