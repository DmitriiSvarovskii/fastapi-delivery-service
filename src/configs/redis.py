from pydantic_settings import SettingsConfigDict

from .base import BaseConfig


class RedisSettings(BaseConfig):
    model_config = SettingsConfigDict(
        env_prefix='REDIS_',
    )
    URL: str


redis_settings = RedisSettings()
