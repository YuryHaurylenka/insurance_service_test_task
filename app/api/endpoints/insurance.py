from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.insurance import create_insurance_request
from app.db.session import get_db
from app.models.tariff import Tariff
from app.schemas.insurance import InsuranceCreate, InsuranceResponse

router = APIRouter()


@router.post("/", response_model=InsuranceResponse)
async def calculate_and_log_insurance(
    request: InsuranceCreate, db: AsyncSession = Depends(get_db)
):
    """
    Calculate insurance cost and log the request.
    """
    calc_date = date.today()

    query = select(Tariff).where(
        Tariff.cargo_type == request.cargo_type,
        Tariff.valid_from <= calc_date,
        Tariff.valid_to >= calc_date,
    )
    result = await db.execute(query)
    tariff = result.scalars().first()

    if not tariff:
        raise HTTPException(
            status_code=404,
            detail=f"No valid tariff found for cargo type '{request.cargo_type}' on {calc_date}",
        )

    insurance_cost = request.declared_value * tariff.rate

    insurance_request = await create_insurance_request(
        db, insurance_data=request, insurance_cost=insurance_cost
    )

    return InsuranceResponse(
        id=insurance_request.id,
        cargo_type=insurance_request.cargo_type,
        declared_value=insurance_request.declared_value,
        insurance_cost=insurance_request.insurance_cost,
        timestamp=insurance_request.timestamp,
    )
