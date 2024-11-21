from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.tariff import CargoType


class InsuranceRequest(Base):
    """
    Model for logging insurance calculation requests.
    """

    __tablename__ = "insurance_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cargo_type: Mapped[CargoType] = mapped_column(Enum(CargoType), nullable=False)
    declared_value: Mapped[float] = mapped_column(Float, nullable=False)
    insurance_cost: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
