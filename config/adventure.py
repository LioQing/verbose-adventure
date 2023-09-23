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

    class Config:
        env_prefix = "ADVENTURE_"
        env_file = ".env"


adventure_config = AdventureConfig()
