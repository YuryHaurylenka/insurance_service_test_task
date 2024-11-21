from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from app.models.tariff import CargoType


class InsuranceBase(BaseModel):
    cargo_type: CargoType = Field(...)
    declared_value: float = Field(..., ge=0)


class InsuranceCreate(InsuranceBase):
    user_id: Optional[int] = None


class InsuranceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cargo_type: CargoType
    declared_value: float
    insurance_cost: float
    timestamp: datetime
    user_id: Optional[int] = None
