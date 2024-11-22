from datetime import date, timedelta
from typing import Dict, List

from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tariff import CargoType, Tariff
from app.schemas.tariff import TariffCreate, TariffJsonItem
from .kafka import add_to_log_buffer
from app.core.config import settings
import logging

logger = logging.getLogger("tariff_service")


async def validate_tariff_dates(
    session: AsyncSession,
    cargo_type: CargoType,
    valid_from: date,
    valid_to: date,
):
    """
    Validates that the date range does not overlap with existing tariffs for the same cargo type.
    """
    overlapping_tariff_query = select(Tariff).where(
        Tariff.cargo_type == cargo_type,
        or_(
            and_(Tariff.valid_from <= valid_to, Tariff.valid_to >= valid_from),
            and_(Tariff.valid_to >= valid_from, Tariff.valid_from <= valid_to),
        ),
    )
    result = await session.execute(overlapping_tariff_query)
    overlapping_tariff = result.scalars().first()

    if overlapping_tariff:
        raise HTTPException(
            status_code=400,
            detail=(
                f"A tariff for {cargo_type} already exists for the "
                f"period {overlapping_tariff.valid_from} to {overlapping_tariff.valid_to}."
            ),
        )


async def load_tariffs_from_json(
    session: AsyncSession,
    tariffs_data: Dict[date, List[TariffJsonItem]],
):
    """
    Load tariffs from a JSON-like structure and save them to the database.
    """
    async with session.begin():  # Начинаем транзакцию
        for valid_from, tariffs in tariffs_data.items():
            if not isinstance(valid_from, date):
                raise TypeError(
                    f"Expected 'date' for valid_from, got {type(valid_from).__name__}"
                )

            valid_to = valid_from + timedelta(days=30)

            for tariff in tariffs:
                tariff_data = TariffCreate(
                    cargo_type=CargoType(tariff.cargo_type),
                    rate=tariff.rate,
                    valid_from=valid_from,
                    valid_to=valid_to,
                )

                await validate_tariff_dates(
                    session=session,
                    cargo_type=tariff_data.cargo_type,
                    valid_from=tariff_data.valid_from,
                    valid_to=tariff_data.valid_to,
                )

                new_tariff = Tariff(
                    cargo_type=tariff_data.cargo_type,
                    rate=tariff_data.rate,
                    valid_from=tariff_data.valid_from,
                    valid_to=tariff_data.valid_to,
                )
                session.add(new_tariff)

                try:
                    await add_to_log_buffer(
                        session=session,
                        topic=settings.kafka_topic_tariffs,
                        action="LOAD_TARIFF",
                        details=tariff_data.dict(),
                        user_id=None,
                    )
                except Exception as e:
                    logger.error(f"Failed to log tariff load event: {e}")
                    raise HTTPException(
                        status_code=500, detail="Failed to log tariff event to Kafka."
                    )

        logger.info(f"Successfully loaded tariffs: {len(tariffs_data)} entries.")
