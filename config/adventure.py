from pydantic import Field
from pydantic_settings import BaseSettings

from .logger import logger_config


class AdventureConfig(BaseSettings):
    """Configurations for Adventure"""

    log_level: str = Field(logger_config.level)
    system_message: str = Field(
        "You are a DnD Dungeon Master. You are creating a new adventure for"
        " your user. You either respond to the user's action or create a new"
        " event or action for user if the user is not sure what to do next. "
        " Give only 2 to 3 sentences, do not list actions for user to choose"
        " from."
    )
    start_message: str = Field("You may start the story however you like.")
    base_summary_system_message: str = Field(
        "You are an assistant to summarize a JSON list of messages between an"
        " assistant and a user. Make sure to include any factual information"
        " and name in the conversation messages, don't make up anything not"
        " mentioned in the conversation messages. Each sentence consists of"
        " about 10 to 30 words. You should always refer to the assistant in"
        " second person perspective, as 'you'."
    )
    prev_summary_system_message: str = (
        "Describe the previous summary using 1 sentence."
    )
    env_summary_system_message: str = (
        "Describe the conversation messages using 3 sentences."
    )
    default_choice_index: int = Field(0)

    @property
    def summary_system_message(self) -> str:
        """Get the summary system message"""
        return (
            self.base_summary_system_message
            + " "
            + self.prev_summary_system_message
            + " "
            + self.env_summary_system_message
        )

    @property
    def summary_system_message_no_prev(self) -> str:
        """Get the summary system message without previous summary"""
        return (
            self.base_summary_system_message
            + " "
            + self.env_summary_system_message
        )

    class Config:
        env_prefix = "ADVENTURE_"
        env_file = ".env"


adventure_config = AdventureConfig()
