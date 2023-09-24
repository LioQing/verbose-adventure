from pydantic import Field
from pydantic_settings import BaseSettings


class LoggerConfig(BaseSettings):
    """Logger config"""

    level: str = Field("INFO")

    class Config:
        env_prefix = "LOGGER_"
        env_file = ".env"


logger_config = LoggerConfig()
