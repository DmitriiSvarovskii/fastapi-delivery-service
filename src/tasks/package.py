import asyncio
import logging

from celery import Celery

from src.db.mysql import async_session_maker
from src.services.delivery_calculator import DeliveryCostCalculator
from src.repositories import PackageRepository
from src.schemas import PackageCreate
from src.configs import task_settings
from src.utils.logging import configure_logging


configure_logging()
logger = logging.getLogger(__name__)

celery_app = Celery("tasks")


@celery_app.task(name="create_package_task", bind=True)
def create_package_task(
    self,
    package_uuid: str,
    session_id: str,
    name: str,
    weight: float,
    type_id: int,
    content_value_usd: float
):
    """
    Задача Celery: рассчитывает стоимость доставки и сохраняет запись.
    Логи:
      - INFO: начало и успешное завершение этапов
      - ERROR: ошибки расчёта и записи в БД с трассировкой
    """
    async def process():
        logger.info("Начало расчёта стоимости для посылки %s", package_uuid)
        try:
            delivery_cost = await DeliveryCostCalculator().calculate(
                weight=weight,
                content_value_usd=content_value_usd
            )
            logger.info(
                "Стоимость для посылки %s рассчитана: %s ₽",
                package_uuid, delivery_cost
            )
        except Exception as e:
            logger.exception(
                "Не удалось рассчитать стоимость для %s",
                package_uuid,
                exc_info=True
            )
            raise self.retry(
                exc=e,
                countdown=task_settings.calculator_retry_countdown,
                max_retries=task_settings.calculator_max_retries
            )

        logger.info("Сохраняем посылку %s в БД", package_uuid)
        package = PackageCreate(
            uuid=package_uuid,
            session_id=session_id,
            name=name,
            weight=weight,
            type_id=type_id,
            content_value_usd=content_value_usd,
            delivery_cost_rub=delivery_cost
        )
        try:
            async with async_session_maker() as session:
                await PackageRepository.create_package(
                    data=package,
                    session=session
                )
            logger.info("Посылка %s успешно сохранена в БД", package_uuid)
        except Exception as e:
            logger.exception(
                "Ошибка при сохранении посылки %s в БД",
                package_uuid,
                exc_info=True
            )
            raise self.retry(
                exc=e,
                countdown=task_settings.db_retry_countdown,
                max_retries=task_settings.db_max_retries
            )

    return asyncio.run(process())
