from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.insurance import create_insurance_request
from app.models.tariff import Tariff
from app.schemas.insurance import InsuranceCreate, InsuranceResponse


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

    return InsuranceResponse(
        id=insurance_request.id,
        cargo_type=insurance_request.cargo_type,
        declared_value=insurance_request.declared_value,
        insurance_cost=insurance_request.insurance_cost,
        timestamp=insurance_request.timestamp,
    )


async def get_valid_tariff(
    db: AsyncSession, cargo_type: str, calc_date: date
) -> Tariff:
    query = select(Tariff).where(
        Tariff.cargo_type == cargo_type,
        Tariff.valid_from <= calc_date,
        Tariff.valid_to >= calc_date,
    )
    result = await db.execute(query)
    tariff = result.scalars().first()

    if not tariff:
        raise HTTPException(
            status_code=404,
            detail=f"No valid tariff found for cargo type '{cargo_type}' on {calc_date}",
        )

    return tariff
