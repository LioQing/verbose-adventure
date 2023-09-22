from pydantic import Field
from pydantic_settings import BaseSettings


class OpenAIConfig(BaseSettings):
    """Configurations for OpenAI API"""

    api_type: str = Field("azure")
    version: str = Field("2023-05-15")
    key: str
    url: str

    class Config:
        env_prefix = "OPENAI_"
        env_file = ".env"


open_ai_config = OpenAIConfig()
