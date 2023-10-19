from pydantic import Field

from . import BaseConfig


class LoggerConfig(BaseConfig):
    """Logger config"""

    level: str = Field("INFO")

    class Config:
        env_prefix = "LOGGER_"
        env_file = ".env"


logger_config = LoggerConfig()
