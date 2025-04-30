import logging

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.mysql import get_async_session
from src.repositories import PackageTypeRepository
from src.schemas import PackageTypeRead
from src.docs import package_type_docs

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/package-type",
    tags=["package-type"],
)


@router.get(
    "/",
    response_model=list[PackageTypeRead],
    status_code=status.HTTP_200_OK,
    summary=package_type_docs.GET_PACKAGE_TYPES_SUMMARY,
    description=package_type_docs.GET_PACKAGE_TYPES_DESCRIPTION,
)
async def list_package_types(
    session: AsyncSession = Depends(get_async_session),
):
    try:
        types = await PackageTypeRepository.get_package_types(session=session)
        return types

    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "Ошибка при получении списка типов посылок", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось получить список типов посылок"
        )
