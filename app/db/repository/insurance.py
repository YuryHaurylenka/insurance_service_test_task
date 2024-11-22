from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.insurance import InsuranceRequest
from app.schemas.insurance import InsuranceCreate


async def create_insurance_request(
    session: AsyncSession, insurance_data: InsuranceCreate, insurance_cost: float
) -> InsuranceRequest:
    """
    Create a new insurance calculation request in the database.
    """
    insurance_request = InsuranceRequest(
        cargo_type=insurance_data.cargo_type,
        declared_value=insurance_data.declared_value,
        insurance_cost=insurance_cost,
        user_id=insurance_data.user_id,
    )
    session.add(insurance_request)
    return insurance_request


async def get_insurance_requests(session: AsyncSession) -> list[InsuranceRequest]:
    """
    Retrieve all insurance calculation requests from the database.
    """
    result = await session.execute(select(InsuranceRequest))
    return list(result.scalars().all())
