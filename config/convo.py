from pydantic import Field
from pydantic_settings import BaseSettings

from .logger import logger_config


class ConvoConfig(BaseSettings):
    """Configurations for Convo"""

    log_level: str = Field(logger_config.level)
    summary_interval: int = Field(5)
    history_length: int = Field(5)
    base_summary_system_message: str = Field(
        "You are an assistant to summarize a JSON list of messages between an"
        " assistant and a user, where the assistant is a DnD Dungeon Master"
        " and user is the player. Make sure to include any factual information"
        " and name in the story, don't make up anything not mentioned in the"
        " story. Each sentence consists of about 10 to 30 words."
    )
    prev_summary_system_message: str = (
        "Describe the previous summary using 1 sentence."
    )
    env_summary_system_message: str = (
        "Describe the environment and circumstances of the story using 3"
        " sentences."
    )
    model: str
    deployment: str

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
        env_prefix = "CONVO_"
        env_file = ".env"


convo_config = ConvoConfig()
