from datetime import date
from pydantic import BaseModel, ConfigDict, Field

from app.models.tariff import CargoType


class TariffBase(BaseModel):
    """
    Base schema for Tariff.
    """

    cargo_type: CargoType = Field(...)
    rate: float = Field(..., ge=0)
    valid_from: date
    valid_to: date


class TariffCreate(TariffBase):
    pass


class TariffUpdate(TariffBase):
    pass


class TariffUpdatePartial(BaseModel):
    cargo_type: CargoType | None = Field(None)
    rate: float | None = Field(None, ge=0)
    valid_from: date | None = None
    valid_to: date | None = None


class TariffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cargo_type: CargoType
    rate: float
    valid_from: date
    valid_to: date
