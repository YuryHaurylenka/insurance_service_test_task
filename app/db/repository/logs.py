from sqlalchemy.ext.asyncio import AsyncSession

from app.models.logs import ActionLog


async def save_action_log(
    session: AsyncSession, action: str, payload: dict, user_id: int | None = None
) -> ActionLog:
    """
    Save an action log to the database.
    """
    log_entry = ActionLog(
        action=action,
        payload=payload,
        user_id=user_id,
    )
    session.add(log_entry)
    await session.commit()
    await session.refresh(log_entry)
    return log_entry
