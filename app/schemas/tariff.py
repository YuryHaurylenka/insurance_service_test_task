from datetime import date
from typing import Dict, List

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


class TariffJsonItem(BaseModel):
    cargo_type: str = Field(..., description="Type of cargo (e.g., 'Glass', 'Other').")
    rate: float = Field(..., description="Rate for the cargo type.")


class TariffJsonInput(BaseModel):
    tariffs: dict[date, list[TariffJsonItem]] = Field(
        ...,
        example={
            "2024-11-21": [
                {"cargo_type": "Glass", "rate": 0.04},
                {"cargo_type": "Other", "rate": 0.01},
            ],
            "2024-11-22": [
                {"cargo_type": "Metal", "rate": 0.03},
                {"cargo_type": "Wood", "rate": 0.02},
            ],
        },
    )


class TariffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cargo_type: CargoType
    rate: float
    valid_from: date
    valid_to: date
