from pydantic import Field

from . import BaseConfig


class ConvoConfig(BaseConfig):
    """Configurations for Convo"""

    summary_interval: int = Field(5)
    history_length: int = Field(5)

    class Config:
        env_prefix = "CONVO_"
        env_file = ".env"


convo_config = ConvoConfig()
