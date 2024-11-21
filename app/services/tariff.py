from datetime import date

from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tariff import CargoType, Tariff


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
