from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_serializer
from pydantic.json_schema import SkipJsonSchema

from .package_types import PackageTypeRead


class PackageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: Optional[SkipJsonSchema[str]] = None
    uuid: Optional[SkipJsonSchema[str]] = None
    name: str
    weight: float
    type_id: int
    content_value_usd: float
    delivery_cost_rub: Optional[SkipJsonSchema[float]] = None


class PackageCreate(PackageBase):
    pass


class PackageRead(PackageBase):
    id: int
    delivery_cost_rub: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    package_type: PackageTypeRead

    @field_serializer("delivery_cost_rub")
    def serialize_delivery_cost(self, v: Optional[float], _info):
        if v is None:
            return "Не рассчитано"
        return v
