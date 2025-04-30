from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.mysql import Base, intpk, str_64, created_at, updated_at

if TYPE_CHECKING:
    from .package_types import PackageType


class Package(Base):
    __tablename__ = "packages"

    id: Mapped[intpk]
    uuid: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, index=True)
    session_id: Mapped[str_64] = mapped_column(index=True)
    name: Mapped[str_64]
    weight: Mapped[float]
    type_id: Mapped[int] = mapped_column(
        ForeignKey("package_types.id", ondelete="CASCADE"))
    content_value_usd: Mapped[float | None]
    delivery_cost_rub: Mapped[float] = mapped_column(
        nullable=True
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at | None]

    package_type: Mapped['PackageType'] = relationship(
        back_populates="package"
    )
