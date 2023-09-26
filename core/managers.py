from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from django.db.models import Manager

from engine import models as engine_models

from .enums import ChatcmplKind

if TYPE_CHECKING:
    from .models import Adventure, Chatcmpl, Choice, Message, Summary


class MessageManager(Manager):
    """Manager for Message"""

    def create_from_engine_message(
        self, adventure: "Adventure", message: engine_models.Message
    ) -> "Message":
        """
        Create a Message from an engine Message

        Args:
            adventure: The adventure
            message: The engine Message

        Returns:
            The created Message
        """
        from .models import Message

        message = Message.from_engine_message(adventure, message)
        message.save()
        return message

    def get_latest_n_messages(
        self, adventure: "Adventure", n: int
    ) -> List["Message"]:
        """
        Get the latest n messages for an adventure

        Args:
            adventure: The adventure
            n: The number of messages

        Returns:
            The list of messages
        """
        curr = adventure.latest_message
        if curr is None:
            return []

        messages = []
        for _ in range(n):
            messages.append(curr)
            curr = curr.prev
            if curr is None:
                break
        return messages[::-1]


class SummaryManager(Manager):
    """Manager for Summary"""

    def create_from_engine_summary(
        self, adventure: "Adventure", summary: engine_models.Message
    ) -> "Summary":
        """
        Create a Summary from an engine Summary

        Args:
            adventure: The adventure
            summary: The engine summary Message

        Returns:
            The created Summary
        """
        from .models import Summary

        summary = Summary.from_engine_summary(adventure.id, summary)
        summary.save()
        return summary


class ChoiceManager(Manager):
    """Manager for Choice"""

    def create_from_engine_choice(
        self,
        chatcmpl: "Chatcmpl",
        message: Optional["Message"],
        summary: Optional["Summary"],
        choice: engine_models.Choice,
    ) -> "Choice":
        """
        Create a Choice from an engine Choice

        Args:
            adventure: The adventure ID
            message: The message ID
            summary: The summary ID
            choice: The engine Choice

        Returns:
            The created Choice
        """
        from .models import Choice

        choice = Choice.from_engine_choice(chatcmpl, message, summary, choice)
        choice.save()
        return choice


class ChatcmplManager(Manager):
    """Manager for Chatcmpl"""

    def create_from_engine_chatcmpl(
        self,
        adventure: "Adventure",
        summary: Optional["Summary"],
        messages: List["Message"],
        chatcmpl: engine_models.Chatcmpl,
        is_summary: bool,
        choice_index: int,
    ) -> "Chatcmpl":
        """
        Create a Chatcmpl from an engine Chatcmpl

        It also creates the related Messages or Summary, and Choices

        Args:
            adventure: The adventure
            summary: The summary
            messages: The messages
            chatcmpl: The engine Chatcmpl
            is_summary: It is a summary if True, else it is a message
            choice_index: The index of the chosen choice

        Returns:
            The created Chatcmpl
        """
        from .models import Chatcmpl, Choice, Message, Summary

        # Create chatcmpl
        chatcmpl_model = Chatcmpl.objects.create(
            id=chatcmpl.id,
            adventure=adventure,
            summary=summary,
            kind=ChatcmplKind.SUMMARY if is_summary else ChatcmplKind.MESSAGE,
            object_name=chatcmpl.object,
            created_at=datetime.fromtimestamp(chatcmpl.created),
            model=chatcmpl.model,
            completion_tokens=chatcmpl.usage.completion_tokens,
            prompt_tokens=chatcmpl.usage.prompt_tokens,
        )
        chatcmpl_model.messages.set(messages)

        for i, choice in enumerate(chatcmpl.choices):
            # Create messages if it is selected
            summary = None
            message = None
            if i == choice_index:
                if is_summary:
                    summary = Summary.objects.create_from_engine_summary(
                        adventure, choice.message
                    )
                else:
                    message = Message.objects.create_from_engine_message(
                        adventure, choice.message
                    )

            # Create choice
            choice = Choice.objects.create_from_engine_choice(
                chatcmpl_model, message, summary, choice
            )

        return chatcmpl_model
