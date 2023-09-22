from pydantic import Field
from pydantic_settings import BaseSettings


class AdventureConfig(BaseSettings):
    """Configurations for Adventure"""

    log_level: str = Field("INFO")
    system_message: str = Field(
        "You are a DnD Dungeon Master. You are creating a new adventure for"
        " your user. You either respond to the user's action or create a new"
        " event or action for user if the user is not sure what to do next. "
        " Give only 2 to 3 sentences, do not list actions for user to choose"
        " from."
    )

    class Config:
        env_prefix = "ADVENTURE_"
        env_file = ".env"


adventure_config = AdventureConfig()
