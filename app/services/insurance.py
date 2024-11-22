from datetime import date

from fastapi import HTTPException
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.insurance import create_insurance_request
from app.models.tariff import CargoType, Tariff
from app.schemas.insurance import InsuranceCreate, InsuranceResponse
from app.schemas.tariff import TariffResponse


async def calculate_insurance_service(
    request: InsuranceCreate, db: AsyncSession
) -> InsuranceResponse:
    calc_date = date.today()

    tariff = await get_valid_tariff(db, request.cargo_type, calc_date)
    insurance_cost = request.declared_value * tariff.rate

    insurance_request = await create_insurance_request(
        db, insurance_data=request, insurance_cost=insurance_cost
    )

    await db.commit()
    await db.refresh(insurance_request)

    await insurance_request.log_creation()

    tariff_response = TariffResponse(
        id=tariff.id,
        cargo_type=tariff.cargo_type,
        rate=tariff.rate,
        valid_from=tariff.valid_from,
        valid_to=tariff.valid_to,
    )

    return InsuranceResponse(
        id=insurance_request.id,
        cargo_type=insurance_request.cargo_type,
        declared_value=insurance_request.declared_value,
        insurance_cost=insurance_request.insurance_cost,
        timestamp=insurance_request.timestamp,
        tariff=tariff_response,
    )


async def get_valid_tariff(
    db: AsyncSession, cargo_type: CargoType, calc_date: date
) -> Tariff:
    query_current = (
        select(Tariff)
        .where(
            Tariff.cargo_type == cargo_type,
            Tariff.valid_from <= calc_date,
            Tariff.valid_to >= calc_date,
        )
        .order_by(desc(Tariff.valid_from))
    )
    result = await db.execute(query_current)
    tariff = result.scalars().first()

    if tariff:
        return tariff

    query_future = (
        select(Tariff)
        .where(
            Tariff.cargo_type == cargo_type,
            Tariff.valid_from > calc_date,
        )
        .order_by(asc(Tariff.valid_from))
    )
    result = await db.execute(query_future)
    future_tariff = result.scalars().first()

    query_past = (
        select(Tariff)
        .where(
            Tariff.cargo_type == cargo_type,
            Tariff.valid_to < calc_date,
        )
        .order_by(desc(Tariff.valid_to))
    )
    result = await db.execute(query_past)
    past_tariff = result.scalars().first()

    if future_tariff and past_tariff:
        delta_future = (future_tariff.valid_from - calc_date).days
        delta_past = (calc_date - past_tariff.valid_to).days

        if delta_future < delta_past:
            tariff = future_tariff
        else:
            tariff = past_tariff
    elif future_tariff:
        tariff = future_tariff
    elif past_tariff:
        tariff = past_tariff
    else:
        raise HTTPException(
            status_code=404,
            detail=f"No valid tariff found for cargo type '{cargo_type}' on {calc_date}",
        )

    return tariff
