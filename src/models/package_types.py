from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.mysql import Base, intpk, str_64

if TYPE_CHECKING:
    from .packages import Package


class PackageType(Base):
    __tablename__ = "package_types"

    id: Mapped[intpk]
    name: Mapped[str_64] = mapped_column(unique=True)

    package: Mapped[list['Package']] = relationship(
        back_populates="package_type")
