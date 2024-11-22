from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.insurance import InsuranceCreate, InsuranceResponse
from app.services.insurance import calculate_insurance_service

router = APIRouter()


@router.post("/", response_model=InsuranceResponse)
async def calculate_and_log_insurance(
    request: InsuranceCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate insurance cost and log the request.
    """
    return await calculate_insurance_service(request, db)
