from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tariff import Tariff
from app.schemas.tariff import TariffCreate, TariffUpdate
from app.services.tariff import validate_tariff_dates


async def get_all_tariffs(session: AsyncSession) -> list[Tariff]:
    """
    Retrieve all tariffs from the database.
    """
    stmt = select(Tariff).order_by(Tariff.id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_tariff_by_id(session: AsyncSession, tariff_id: int) -> Tariff | None:
    """
    Retrieve a tariff by its ID.
    """
    return await session.get(Tariff, tariff_id)


async def create_tariff(
    session: AsyncSession, tariff_in: TariffCreate, user_id: int | None = None
) -> Tariff:
    """
    Create a new tariff and log the action to Kafka.
    """
    await validate_tariff_dates(
        session=session,
        cargo_type=tariff_in.cargo_type,
        valid_from=tariff_in.valid_from,
        valid_to=tariff_in.valid_to,
    )

    tariff = Tariff(
        cargo_type=tariff_in.cargo_type,
        rate=tariff_in.rate,
        valid_from=tariff_in.valid_from,
        valid_to=tariff_in.valid_to,
    )

    session.add(tariff)
    try:
        await session.commit()
        await session.refresh(tariff)
        await tariff.log_creation()
    except IntegrityError as e:
        await session.rollback()
        raise ValueError(f"Error saving tariff: {str(e)}")

    return tariff


async def update_tariff(
    session: AsyncSession,
    tariff: Tariff,
    tariff_update: TariffUpdate,
    partial: bool = False,
) -> Tariff:
    """
    Update an existing tariff record.

    If `partial=True`, update only the fields provided in `tariff_update`.
    If `partial=False`, replace all fields with the provided data.
    """
    update_data = tariff_update.dict(exclude_unset=partial)

    for key, value in update_data.items():
        setattr(tariff, key, value)

    await session.commit()
    await session.refresh(tariff)
    await tariff.log_update(session, update_data)

    return tariff


async def delete_tariff(session: AsyncSession, tariff: Tariff) -> None:
    """
    Delete a tariff from the database.
    """
    await tariff.log_deletion(session)
    await session.delete(tariff)
    await session.commit()
