import httpx
import logging

from src.configs import calculator_settings, cbr_api_settings
from src.db.redis import RedisClient

logger = logging.getLogger(__name__)


class DeliveryCostCalculator:
    """
    Калькулятор стоимости доставки.

    Методы:
      - _fetch_usd_rate_from_api():
          ERROR при сетевых ошибках или неверном HTTP-статусе.
          INFO при успешном получении курса.
      - get_usd_rate():
          DEBUG при попытке чтения из кэша.
          WARNING при некорректном закэшированном значении.
          INFO при получении и кэшировании нового курса.
          ERROR при ошибках работы с Redis.
      - calculate():
          Возвращает рассчитанную стоимость, без логов.
    """

    def _fetch_usd_rate_from_api(self) -> float:
        try:
            resp = httpx.get(
                cbr_api_settings.CBR_API_URL,
                timeout=calculator_settings.http_timeout
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError:
            logger.exception(
                "Не удалось получить курс USD, неверный ответ API",
                exc_info=True
            )
            raise
        except httpx.RequestError:
            logger.exception(
                "Сетевая ошибка при запросе курса USD",
                exc_info=True
            )
            raise

        data = resp.json()
        usd = data["Valute"]["USD"]
        rate = usd["Value"] / usd["Nominal"]
        logger.info("Курс USD от API: %s", rate)
        return rate

    async def get_usd_rate(self) -> float:
        """
        Получить курс USD:
          - сначала пытается из Redis;
          - если нет или невалидно — от API и обновляет кэш.
        Исключения:
          - httpx.RequestError, HTTPStatusError
          - ошибки RedisClient.get_client / set / close
        """
        try:
            r = await RedisClient.get_client()
        except Exception:
            logger.error(
                "Не удалось подключиться к Redis",
                exc_info=True
            )
            raise

        try:
            logger.debug("Пробуем получить курс USD из кэша")
            cached = await r.get(name=calculator_settings.redis_key)
            if cached:
                try:
                    rate = float(cached)
                    logger.info("Курс USD из кэша: %s", rate)
                    return rate
                except ValueError:
                    logger.warning(
                        "Некорректное значение курса в кэше: %s",
                        cached
                    )

            rate = self._fetch_usd_rate_from_api()
            try:
                await r.set(
                    name=calculator_settings.redis_key,
                    value=rate,
                    ex=calculator_settings.cache_ttl
                )
                logger.debug(
                    "Курс USD сохранён в кэше на %s сек.",
                    calculator_settings.cache_ttl
                )
            except Exception:
                logger.error(
                    "Не удалось записать курс USD в Redis",
                    exc_info=True
                )
            return rate

        finally:
            try:
                await r.close()
            except Exception:
                logger.warning(
                    "Ошибка при закрытии соединения с Redis",
                    exc_info=True
                )

    async def calculate(
        self,
        weight: float,
        content_value_usd: float
    ) -> float:
        """
        Рассчитывает стоимость доставки с учётом текущего курса USD.
        """
        usd_to_rub = await self.get_usd_rate()
        cost = (
            weight * calculator_settings.weight_factor +
            content_value_usd * calculator_settings.value_factor
        ) * usd_to_rub
        rounded = round(cost, 2)
        return rounded
