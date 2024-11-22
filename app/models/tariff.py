import enum

from sqlalchemy import Date, Enum, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.models.base import Base
from app.services.kafka import add_to_log_buffer


class CargoType(enum.Enum):
    GLASS = "Glass"
    METAL = "Metal"
    WOOD = "Wood"
    OTHER = "Other"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value_upper = value.upper()
            for member in cls:
                if member.value == value_upper:
                    return member
        return None


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

    async def log_creation(self):
        """
        Log the creation of a tariff.
        """
        await add_to_log_buffer(
            topic=settings.kafka_topic_tariffs,
            action="CREATE_TARIFF",
            details={
                "id": self.id,
                "cargo_type": self.cargo_type.value,
                "rate": self.rate,
                "valid_from": self.valid_from.isoformat(),
                "valid_to": self.valid_to.isoformat(),
            },
        )

    async def log_update(self, updated_fields: dict):
        """
        Log the update of a tariff.
        """
        await add_to_log_buffer(
            topic=settings.kafka_topic_tariffs,
            action="UPDATE_TARIFF",
            details={
                "id": self.id,
                **updated_fields,
            },
        )

    async def log_deletion(self):
        """
        Log the deletion of a tariff.
        """
        await add_to_log_buffer(
            topic=settings.kafka_topic_tariffs,
            action="DELETE_TARIFF",
            details={
                "id": self.id,
                "cargo_type": self.cargo_type.value,
            },
        )
