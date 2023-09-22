from pydantic import Field
from pydantic_settings import BaseSettings


class MainConfig(BaseSettings):
    """Main configurations"""

    enable_log: bool = Field(False)

    class Config:
        env_prefix = "MAIN_"
        env_file = ".env"


main_config = MainConfig()
