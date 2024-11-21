import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.kafka import produce_message
from app.db.repository.logs import save_action_log
from .kafka import convert_to_serializable

logger = logging.getLogger("kafka")


async def log_event(
    session: AsyncSession,
    topic: str,
    action: str,
    details: dict,
    user_id: Optional[int] = None,
):
    """
    Log an event to Kafka and save it in the database.
    """
    try:
        serialized_details = convert_to_serializable(details)
        message = {
            "user_id": user_id,
            "action": action,
            "details": serialized_details,
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(f"Logging event to Kafka topic '{topic}': {message}")
        produce_message(topic, message)

        await save_action_log(session, action, serialized_details, user_id)

        logger.info(f"Event logged successfully to Kafka and database: {message}")
    except Exception as e:
        logger.error(f"Failed to log event: {e}")
        raise
