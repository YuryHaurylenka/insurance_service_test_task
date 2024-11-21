from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class InsuranceBase(BaseModel):
    cargo_type: str = Field(..., max_length=128)
    declared_value: float = Field(..., ge=0)


class InsuranceCreate(InsuranceBase):
    pass


class InsuranceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cargo_type: str
    declared_value: float
    insurance_cost: float
    timestamp: datetime
