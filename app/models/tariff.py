import enum

from sqlalchemy import Date, Enum, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CargoType(enum.Enum):
    GLASS = "Glass"
    METAL = "Metal"
    WOOD = "Wood"
    OTHER = "Other"


class Tariff(Base):
    """
    Model representing insurance tariffs for different types of cargo.
    """

    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cargo_type: Mapped[CargoType] = mapped_column(
        Enum(CargoType), nullable=False, index=True
    )
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    valid_from: Mapped[Date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[Date] = mapped_column(Date, nullable=False)
