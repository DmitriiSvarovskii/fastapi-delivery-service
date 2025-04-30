from .base import BaseConfig


class SessionCookieSettings(BaseConfig):
    SESSION_MAX_AGE: int = 60 * 60 * 24
    COOKIE_SECRET_KEY: str
    COOKIE_NAME: str = "session_id"


session_cookie_settings = SessionCookieSettings()
