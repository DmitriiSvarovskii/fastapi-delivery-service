from pydantic import BaseModel, ConfigDict


class PackageTypeBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class PackageTypeCreate(PackageTypeBase):
    pass


class PackageTypeRead(PackageTypeBase):
    id: int
