from datetime import datetime
from typing import List, Optional

from django.db.models import Manager

from engine import models as engine_models

from . import models


class MessageManager(Manager):
    """Manager for Message"""

    def from_engine_message(
        adventure_id: int, message: engine_models.Message
    ) -> models.Message:
        """
        Create a Message from an engine Message

        Args:
            adventure_id: The adventure ID
            message: The engine Message

        Returns:
            The created Message
        """
        return models.Message(
            adventure_id=adventure_id,
            role=message.role,
            content=message.content,
            name=message.name,
        )


class SummaryManager(Manager):
    """Manager for Summary"""

    def from_engine_summary(
        adventure_id: int, summary: engine_models.Message
    ) -> models.Summary:
        """
        Create a Summary from an engine Summary

        Args:
            adventure_id: The adventure ID
            summary: The engine summary Message

        Returns:
            The created Summary
        """
        return models.Summary(
            summary=summary.content,
        )


class ChoiceManager(Manager):
    """Manager for Choice"""

    def from_engine_choice(
        chatcmpl_id: int,
        message_id: Optional[int],
        summary_id: Optional[int],
        choice: engine_models.Choice,
    ) -> models.Choice:
        """
        Create a Choice from an engine Choice

        Args:
            adventure_id: The adventure ID
            message_id: The message ID
            summary_id: The summary ID
            choice: The engine Choice

        Returns:
            The created Choice
        """
        return models.Choice(
            chatcmpl_id=chatcmpl_id,
            index=choice.index,
            message=message_id,
            summary=summary_id,
            finish_reason=choice.finish_reason,
        )


class ChatcmplManager(Manager):
    """Manager for Chatcmpl"""

    def from_engine_chatcmpl(
        adventure_id: int,
        summary_id: Optional[int],
        message_ids: List[int],
        chatcmpl: engine_models.Chatcmpl,
        is_summary: bool,
        choice_index: int = 0,
    ) -> models.Chatcmpl:
        """
        Create a Chatcmpl from an engine Chatcmpl

        It also creates the related Messages or Summary, and Choices

        Args:
            adventure_id: The adventure ID
            is_summary: It is a summary if True, else it is a message
            chatcmpl: The engine Chatcmpl
            choice_index: The index of the chosen choice

        Returns:
            The created Chatcmpl
        """
        # Create chatcmpl
        chatcmpl = models.Chatcmpl(
            id=chatcmpl.id,
            adventure_id=adventure_id,
            summary_id=summary_id,
            message_ids=message_ids,
            kind=models.ChatcmplKind.SUMMARY
            if is_summary
            else models.ChatcmplKind.MESSAGE,
            object_name=chatcmpl.object,
            created_at=datetime.fromtimestamp(chatcmpl.created),
            model=chatcmpl.model,
            completion_tokens=chatcmpl.usage.completion_tokens,
            prompt_tokens=chatcmpl.usage.prompt_tokens,
        )

        for i, choice in enumerate(chatcmpl.choices):
            # Create messages if it is selected
            summary_id = None
            message_id = None
            if i == choice_index:
                if is_summary:
                    summary = models.Summary.objects.from_engine_summary(
                        adventure_id, choice.message
                    )
                    summary.save()
                    summary_id = summary.id
                else:
                    message = models.Message.objects.from_engine_message(
                        adventure_id, choice.message
                    )
                    message.save()
                    message_id = message.id

            # Create choice
            choice = ChoiceManager.from_engine_choice(
                chatcmpl.id, message_id, summary_id, choice
            )

        return chatcmpl
