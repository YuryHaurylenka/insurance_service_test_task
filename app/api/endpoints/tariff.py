from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.tariff import (
    create_tariff,
    get_all_tariffs,
    get_tariff_by_id,
    update_tariff,
)
from app.db.session import get_db
from app.schemas.tariff import (
    TariffCreate,
    TariffResponse,
    TariffUpdatePartial,
)

router = APIRouter()


async def get_existing_tariff(tariff_id: int, db: AsyncSession):
    """
    Retrieve a tariff by its ID or raise 404 if not found.
    """
    tariff = await get_tariff_by_id(db, tariff_id)
    if not tariff:
        raise HTTPException(
            status_code=404, detail=f"Tariff with ID {tariff_id} not found"
        )
    return tariff


@router.get("/", response_model=list[TariffResponse])
async def list_tariffs(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all tariffs.
    """
    return await get_all_tariffs(db)


@router.get("/{tariff_id}", response_model=TariffResponse)
async def get_tariff(tariff_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a tariff by its ID.
    """
    return await get_existing_tariff(tariff_id, db)


@router.post("/", response_model=TariffResponse)
async def add_tariff(tariff_in: TariffCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new tariff.
    """
    return await create_tariff(db, tariff_in)


@router.put("/{tariff_id}", response_model=TariffResponse)
async def update_tariff_full(
    tariff_id: int,
    tariff_update: TariffUpdatePartial,
    db: AsyncSession = Depends(get_db),
):
    """
    Fully update an existing tariff.
    """
    tariff = await get_existing_tariff(tariff_id, db)
    return await update_tariff(db, tariff, tariff_update, partial=False)


@router.patch("/{tariff_id}", response_model=TariffResponse)
async def update_tariff_partial(
    tariff_id: int,
    tariff_update: TariffUpdatePartial,
    db: AsyncSession = Depends(get_db),
):
    """
    Partially update an existing tariff.
    """
    tariff = await get_existing_tariff(tariff_id, db)
    return await update_tariff(db, tariff, tariff_update, partial=True)


@router.delete("/{tariff_id}", response_model=dict)
async def delete_tariff(tariff_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a tariff by its ID.
    """
    tariff = await get_tariff_by_id(db, tariff_id)
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")

    await db.delete(tariff)
    await db.commit()
    return {"status": "success", "message": f"Tariff with ID {tariff_id} deleted"}
