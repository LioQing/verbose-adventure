from pydantic import Field

from . import BaseConfig


class OpenAIConfig(BaseConfig):
    """Configurations for OpenAI API"""

    api_type: str = Field("azure")
    version: str = Field("2023-08-01-preview")
    key: str
    url: str
    model: str
    deployment: str

    class Config:
        env_prefix = "OPENAI_"
        env_file = ".env"


open_ai_config = OpenAIConfig()
