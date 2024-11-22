import asyncio
import logging
from asyncio import Lock
from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional

from app.core.config import settings
from app.core.kafka import produce_message
from app.db.database import db
from app.db.repository.logs import save_action_log

logger = logging.getLogger("app")

LOG_BUFFER: List[Dict] = []
BUFFER_LOCK = Lock()
FLUSH_INTERVAL = settings.flush_interval
BATCH_SIZE = settings.batch_size


def convert_to_serializable(data: dict) -> dict:
    """Converts non-serializable objects (dates, enums, etc.) in a dictionary to serializable formats."""
    for key, value in data.items():
        if isinstance(value, (datetime, date)):
            data[key] = value.isoformat()
        elif isinstance(value, Enum):
            data[key] = value.value
        elif isinstance(value, dict):
            data[key] = convert_to_serializable(value)
        elif isinstance(value, list):
            data[key] = [
                convert_to_serializable(v) if isinstance(v, dict) else v for v in value
            ]
    return data


async def flush_logs_to_kafka():
    """Flush all accumulated logs from the buffer to Kafka and save them to the database."""
    async with BUFFER_LOCK:
        if not LOG_BUFFER:
            return

        batch = LOG_BUFFER[:]
        LOG_BUFFER.clear()

    logger.info(f"Flushing {len(batch)} logs to Kafka and database.")

    session = db.session_factory()

    try:
        async with session.begin():
            for item in batch:
                message = convert_to_serializable(item["message"])
                topic = item["topic"]

                await save_action_log(
                    session,
                    action=message["action"],
                    payload=message["details"],
                    user_id=message["user_id"],
                )

                await produce_message(topic, message)

    except Exception as e:
        logger.error(f"Failed to process log batch: {e}", exc_info=True)
        logger.info("Database transaction rolled back")
    finally:
        await session.close()


async def add_to_log_buffer(
    topic: str, action: str, details: dict, user_id: Optional[int] = None
):
    """
    Adds a log entry to the buffer and triggers a flush if the buffer reaches the batch size.
    """
    should_flush = False

    message = {
        "user_id": user_id,
        "action": action,
        "details": convert_to_serializable(details),
        "timestamp": datetime.utcnow().isoformat(),
    }

    async with BUFFER_LOCK:
        LOG_BUFFER.append({"message": message, "topic": topic})
        logger.info(f"Added log to buffer: {message}")

        if len(LOG_BUFFER) >= BATCH_SIZE:
            logger.info(
                "Batch size limit reached. Will trigger flush after releasing lock."
            )
            should_flush = True

    if should_flush:
        await flush_logs_to_kafka()
        if (
            not hasattr(add_to_log_buffer, "flush_task")
            or add_to_log_buffer.flush_task.done()
        ):
            add_to_log_buffer.flush_task = asyncio.create_task(log_flush_loop())


async def log_flush_loop():
    """
    Adds a log entry to the buffer and triggers a flush if the buffer reaches the flush interval.
    """
    try:
        while True:
            await asyncio.sleep(FLUSH_INTERVAL)
            logger.info("Flush interval reached. Triggering flush.")
            await flush_logs_to_kafka()
    except asyncio.CancelledError:
        logger.info("Log flush loop cancelled.")
    except Exception as e:
        logger.error(f"Error in log flush loop: {e}", exc_info=True)
