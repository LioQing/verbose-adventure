from typing import Any, Dict

from pydantic import Field
from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    """Database configuration"""

    engine: str = Field("django.db.backends.postgresql")
    host: str = Field("")
    port: str = Field("")
    name: str
    user: str
    password: str
    options: Dict[str, Any] = Field(default_factory=dict)

    def to_settings(self) -> Dict[str, Any]:
        """Convert to Django settings format"""
        return {
            "ENGINE": self.engine,
            "HOST": self.host,
            "PORT": self.port,
            "NAME": self.name,
            "USER": self.user,
            "PASSWORD": self.password,
            "OPTIONS": self.options,
        }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "DB_"


db_config = DBConfig()
