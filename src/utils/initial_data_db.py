import asyncio
import logging
from typing import Set

from src.db.mysql import async_session_maker
from src.repositories import PackageTypeRepository
from src.schemas import PackageTypeCreate, PackageTypeRead
from src.utils.logging import configure_logging


configure_logging()
logger = logging.getLogger(__name__)


DEFAULT_PACKAGE_TYPES: list[str] = ["одежда", "электроника", "разное"]


async def seed_package_types() -> None:
    try:
        async with async_session_maker() as session:
            repo = PackageTypeRepository()

            existing: list[PackageTypeRead] = await repo.get_package_types(
                session=session
            )
            existing_names: Set[str] = {pt.name for pt in existing}

            for name in DEFAULT_PACKAGE_TYPES:
                if name not in existing_names:
                    data = PackageTypeCreate(name=name)
                    await repo.create_package_type(data, session=session)
                    logger.info("Добавлен новый тип посылки: %s", name)
    except Exception as e:
        logger.error(
            "Ошибка при инициализации типов посылок: %s",
            e, exc_info=True
        )
        raise


if __name__ == "__main__":
    logger.info("Запуск initial_data_db.seed_package_types()")
    asyncio.run(seed_package_types())
    logger.info("initial_data_db.seed_package_types() завершён успешно")
