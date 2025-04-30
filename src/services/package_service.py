import logging

from typing import Any

from src.schemas.packages import PackageCreate
from src.tasks.package import create_package_task

logger = logging.getLogger(__name__)


class PackageService:
    @staticmethod
    async def enqueue_create(
        pkg_uuid: str,
        session_id: str,
        payload: PackageCreate,
    ) -> None:
        """
        Ставит в очередь задачу на создание посылки.

        Логи:
          - INFO: параметры и факт постановки в очередь
          - ERROR: ошибки при попытке отправить в Celery
        """
        task_args: dict[str, Any] = payload.model_dump(
            exclude={"session_id", "uuid", "delivery_cost_rub"},
        )
        try:
            logger.info(
                "Ставим задачу создания посылки в очередь: %s, %s, %s",
                pkg_uuid, session_id, task_args
            )
            create_package_task.delay(
                package_uuid=pkg_uuid,
                session_id=session_id,
                **task_args,
            )
            logger.debug(
                "Задача create_package_task.delay отправлена: %s", pkg_uuid
            )
        except Exception:
            logger.exception(
                "Не удалось поставить задачу create_package_task для %s",
                pkg_uuid,
                exc_info=True
            )
            raise
