from pydantic import Field
from pydantic_settings import BaseSettings


class MainConfig(BaseSettings):
    """Main configurations"""

    enable_log: bool = Field(False)

    class Config:
        env_prefix = "MAIN_"
        env_file = ".env"


class OpenAIConfig(BaseSettings):
    """Configurations for OpenAI API"""

    api_type: str = Field("azure")
    version: str = Field("2023-05-15")
    key: str
    url: str

    class Config:
        env_prefix = "OPENAI_"
        env_file = ".env"


class ConvoConfig(BaseSettings):
    """Configurations for Convo"""

    log_level: str = Field("INFO")
    log_file: str = Field("./data/convo.json")
    summary_interval: int = Field(5)
    message_history: int = Field(5)
    base_summary_system_message: str = Field(
        "You are an assistant to summarize the JSON list of messages given by"
        " the user. Make sure to mention any factual information and name in"
        " the story. Each sentence consists of about 10 to 30 words."
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


main_config = MainConfig()
open_ai_config = OpenAIConfig()
convo_config = ConvoConfig()
