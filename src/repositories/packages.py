import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Package
from src.schemas import PackageCreate, PackageRead
from src.db.mysql import get_async_session
from src.utils.db_err_decorators import handle_db_errors

logger = logging.getLogger(__name__)


class PackageRepository:
    """Класс для работы с таблицей package."""

    @staticmethod
    @handle_db_errors
    async def create_package(
        data: PackageCreate,
        session: AsyncSession = Depends(get_async_session)
    ) -> dict[str, str]:
        logger.info("Создание посылки: %s", data.model_dump())
        pkg = Package(**data.model_dump())
        session.add(pkg)
        await session.commit()
        logger.info("Посылка создана успешно: UUID=%s", data.uuid)
        return {"status": "success"}

    @staticmethod
    @handle_db_errors
    async def get_package_by_uuid(
        package_uuid: str,
        session_id: str,
        session: AsyncSession = Depends(get_async_session)
    ) -> PackageRead:
        logger.info("Поиск посылки по UUID=%s для session_id=%s",
                    package_uuid, session_id)
        query = (
            select(Package)
            .options(selectinload(Package.package_type))
            .where(
                Package.uuid == package_uuid,
                Package.session_id == session_id
            )
        )
        result = await session.execute(query)
        package = result.scalar()

        if package is None:
            logger.warning(
                "Посылка не найдена: UUID=%s, session_id=%s",
                package_uuid,
                session_id
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Посылка не найдена"
            )

        logger.debug("Найдена посылка: %s", package)
        return package

    @staticmethod
    @handle_db_errors
    async def get_package_by_session_id(
        session: AsyncSession,
        session_id: str,
        type_id: Optional[int] = None,
        calculated: Optional[bool] = None,
        skip: Optional[int] = 0,
        limit: Optional[int] = 10,
    ) -> list[PackageRead]:
        logger.info(
            "Получение списка посылок для session_id=%s, \
                type_id=%s,\
                 calculated=%s, \
                skip=%s, \
                limit=%s",
            session_id, type_id, calculated, skip, limit
        )
        query = (
            select(Package)
            .options(selectinload(Package.package_type))
            .where(Package.session_id == session_id)
            .offset(skip)
            .limit(limit)
        )

        if type_id is not None:
            query = query.where(Package.type_id == type_id)

        if calculated is True:
            query = query.where(Package.delivery_cost_rub.is_not(None))

        result = await session.execute(query)
        packages = result.scalars().all()
        logger.debug("Найдено %d посылок", len(packages))
        return packages
