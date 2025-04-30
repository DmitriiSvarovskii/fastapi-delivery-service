import uuid
import logging

from itsdangerous import Signer, BadSignature
from fastapi import Depends, Cookie, Response, Request

from src.configs import session_cookie_settings
from src.db.redis import RedisClient

logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self):
        self.signer = Signer(session_cookie_settings.COOKIE_SECRET_KEY)
        self.cookie_name = session_cookie_settings.COOKIE_NAME
        self.max_age = session_cookie_settings.SESSION_MAX_AGE

    async def __call__(
        self,
        request: Request,
        response: Response,
        session_cookie: str | None = Cookie(
            default=None,
            alias=session_cookie_settings.COOKIE_NAME,
            include_in_schema=False
        ),
        redis=Depends(RedisClient.get_client),
    ) -> str:

        async def save(sid: str):
            key = f"session:{sid}"
            try:
                await redis.set(key, "", ex=self.max_age)
                logger.debug("Сохранили сессию в Redis: %s", sid)
            except Exception:
                logger.exception(
                    "Не удалось сохранить сессию %s в Redis",
                    sid,
                    exc_info=True
                )
                raise

        # 1) Нет cookie — создаём новую сессию
        if not session_cookie:
            new_sid = str(uuid.uuid4())
            signed = self.signer.sign(new_sid).decode()
            response.set_cookie(
                key=self.cookie_name,
                value=signed,
                max_age=self.max_age,
                httponly=True,
                samesite="lax",
            )
            logger.info("Создана новая сессия: %s", new_sid)
            await save(new_sid)
            return new_sid

        # 2) Есть cookie — проверяем подпись
        try:
            unsigned = self.signer.unsign(session_cookie).decode()
            logger.debug("Проверена подпись существующей сессии: %s", unsigned)
        except BadSignature:
            new_sid = str(uuid.uuid4())
            signed = self.signer.sign(new_sid).decode()
            response.set_cookie(
                key=self.cookie_name,
                value=signed,
                max_age=self.max_age,
                httponly=True,
                samesite="lax",
            )
            logger.warning(
                "Подпись cookie некорректна, выдана новая сессия: %s", new_sid)
            await save(new_sid)
            return new_sid

        key = f"session:{unsigned}"
        try:
            if await redis.exists(key):
                await redis.expire(key, self.max_age)
                logger.debug("Обновлён TTL для сессии %s", unsigned)
            else:
                logger.info(
                    "Сессия %s не найдена в Redis, создаю заново", unsigned)
                await save(unsigned)
        except Exception:
            logger.exception(
                "Ошибка при проверке/обновлении сессии %s в Redis",
                unsigned,
                exc_info=True
            )
            raise

        return unsigned


session_manager = SessionManager()
