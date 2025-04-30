from .base import BaseConfig


class CbrApiSettings(BaseConfig):
    CBR_API_URL: str


cbr_api_settings = CbrApiSettings()
