from .base import BaseConfig


class CelerySettings(BaseConfig):
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str = "rpc://"


celery_settings = CelerySettings()
