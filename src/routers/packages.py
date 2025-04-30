import uuid
import logging

from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import session_manager
from src.db.mysql import get_async_session
from src.repositories import PackageRepository
from src.schemas import PackageCreate, PackageRead
from src.docs import packages_docs
from src.services.package_service import PackageService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/packages",
    tags=["packages"]
)


@router.post(
    "/",
    response_model=str,
    status_code=status.HTTP_202_ACCEPTED,
    summary=packages_docs.CREATE_PACKAGE_SUMMARY,
    description=packages_docs.CREATE_PACKAGE_DESCRIPTION,
)
async def add_package(
    data: PackageCreate,
    session_id: str = Depends(session_manager),
):
    pkg_uuid = str(uuid.uuid4())
    logger.info(
        "Новый запрос на создание посылки: uuid=%s, session_id=%s, payload=%s",
        pkg_uuid, session_id, data.model_dump(exclude_none=True)
    )
    try:
        await PackageService.enqueue_create(
            pkg_uuid=pkg_uuid,
            session_id=session_id,
            payload=data,
        )
        logger.info(
            "Задача на создание посылки %s поставлена в очередь", pkg_uuid)
        return pkg_uuid

    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "Не удалось поставить задачу создания посылки %s",
            pkg_uuid,
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке запроса на создание посылки"
        )


@router.get(
    "/{package_uuid}/",
    response_model=PackageRead,
    status_code=status.HTTP_200_OK,
    summary=packages_docs.GET_PACKAGE_BY_UUID_SUMMARY,
    description=packages_docs.GET_PACKAGE_BY_UUID_DESCRIPTION,
)
async def get_package_by_uuid(
    package_uuid: str,
    session: AsyncSession = Depends(get_async_session),
    session_id: str = Depends(session_manager),
):
    logger.info("Получение посылки по UUID %s для session_id=%s",
                package_uuid, session_id)
    try:
        package = await PackageRepository.get_package_by_uuid(
            package_uuid=package_uuid,
            session_id=session_id,
            session=session
        )
        logger.debug("Найдена посылка: %s", package)
        return package

    except HTTPException:
        raise
    except Exception:
        logger.exception("Ошибка при получении посылки %s",
                         package_uuid, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении данных посылки"
        )


@router.get(
    "/",
    response_model=list[PackageRead],
    status_code=status.HTTP_200_OK,
    summary=packages_docs.LIST_PACKAGES_SUMMARY,
    description=packages_docs.LIST_PACKAGES_DESCRIPTION,
)
async def list_packages(
    type_id: Optional[int] = None,
    calculated: Optional[bool] = True,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    session_id: str = Depends(session_manager),
    session: AsyncSession = Depends(get_async_session),
):
    logger.info(
        "Список посылок: \
            session_id=%s, \
            type_id=%s, \
            calculated=%s, \
            skip=%s, \
            limit=%s",
        session_id, type_id, calculated, skip, limit
    )
    try:
        packages = await PackageRepository.get_package_by_session_id(
            session=session,
            session_id=session_id,
            type_id=type_id,
            calculated=calculated,
            skip=skip,
            limit=limit,
        )
        logger.debug("Получено %d посылок", len(packages))
        return packages

    except HTTPException:
        raise
    except Exception:
        logger.exception("Ошибка при получении списка посылок", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении списка посылок"
        )
