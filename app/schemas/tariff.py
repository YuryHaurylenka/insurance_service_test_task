from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class TariffBase(BaseModel):
    """
    Base schema for Tariff.
    """

    cargo_type: str = Field(..., max_length=128)
    rate: float = Field(..., ge=0)
    valid_from: date
    valid_to: date


class TariffCreate(TariffBase):
    pass


class TariffUpdate(TariffBase):
    pass


class TariffUpdatePartial(BaseModel):
    cargo_type: str | None = Field(None, max_length=128)
    rate: float | None = Field(None, ge=0)
    valid_from: date | None = None
    valid_to: date | None = None


class TariffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cargo_type: str
    rate: float
    valid_from: date
    valid_to: date
