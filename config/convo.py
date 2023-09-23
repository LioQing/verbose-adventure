from pydantic import Field
from pydantic_settings import BaseSettings


class ConvoConfig(BaseSettings):
    """Configurations for Convo"""

    log_level: str = Field("INFO")
    log_file: str = Field("./data/convo.json")
    summary_interval: int = Field(5)
    history_length: int = Field(5)
    base_summary_system_message: str = Field(
        "You are an assistant to summarize the JSON list of messages given by"
        " the user. Make sure to mention any factual information and name in"
        " the story. Do not mention anything not in the story in the JSON"
        " list. Each sentence consists of about 10 to 30 words."
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
