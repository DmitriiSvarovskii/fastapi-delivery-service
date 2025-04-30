import datetime

from typing import Annotated, AsyncGenerator
from sqlalchemy import MetaData, String
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column
from sqlalchemy.pool import NullPool
from src.configs import db_settings


metadata = MetaData()


engine = create_async_engine(db_settings.URL, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


str_64 = Annotated[str, 64]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_64: String(64),
    }


intpk = Annotated[int, mapped_column(primary_key=True, index=True)]

created_at = Annotated[datetime.datetime,
                       mapped_column(default=func.now())]

updated_at = Annotated[datetime.datetime,
                       mapped_column(server_onupdate=func.now())]
