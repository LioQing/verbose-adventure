from pydantic import Field
from pydantic_settings import BaseSettings

from .logger import logger_config


class ConvoConfig(BaseSettings):
    """Configurations for Convo"""

    log_level: str = Field(logger_config.level)
    summary_interval: int = Field(5)
    history_length: int = Field(5)
    model: str
    deployment: str

    class Config:
        env_prefix = "CONVO_"
        env_file = ".env"


convo_config = ConvoConfig()
