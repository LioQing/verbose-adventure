from . import BaseConfig


class AzureAiSearchConfig(BaseConfig):
    """Configurations for OpenAI API"""

    service_name: str
    admin_key: str

    class Config:
        env_prefix = "AZURE_AI_SEARCH_"
        env_file = ".env"


azure_ai_search_config = AzureAiSearchConfig()
