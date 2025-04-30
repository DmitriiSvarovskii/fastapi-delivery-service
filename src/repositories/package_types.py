import logging
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import PackageType
from src.schemas import PackageTypeRead, PackageTypeCreate
from src.db.mysql import get_async_session
from src.utils.db_err_decorators import handle_db_errors

logger = logging.getLogger(__name__)


class PackageTypeRepository:
    """Класс для работы с таблицей package_types."""

    @staticmethod
    @handle_db_errors
    async def get_package_types(
        session: AsyncSession = Depends(get_async_session)
    ) -> list[PackageTypeRead]:
        logger.info("Запрос списка типов посылок")
        query = select(PackageType).order_by(PackageType.id)

        result = await session.execute(query)
        package_types = result.scalars().all()

        logger.debug("Найдено %d типов посылок", len(package_types))
        return package_types

    @staticmethod
    @handle_db_errors
    async def create_package_type(
        data: PackageTypeCreate,
        session: AsyncSession = Depends(get_async_session)
    ) -> dict[str, str]:
        logger.info("Создание типа посылки: %s", data.model_dump())
        pkg = PackageType(**data.model_dump())
        session.add(pkg)
        await session.commit()
        logger.info("Тип посылки '%s' успешно создан", data.name)
        return {"status": "success"}
