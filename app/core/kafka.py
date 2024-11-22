import json
import logging
from typing import Optional

from aiokafka import AIOKafkaProducer

from app.core.config import settings

logger = logging.getLogger("kafka")

producer: Optional[AIOKafkaProducer] = None


async def get_kafka_producer() -> AIOKafkaProducer:
    global producer
    if producer is None:
        producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_broker)
        await producer.start()
        logger.info("Kafka producer started.")
    return producer


async def produce_message(topic: str, message: dict, user_id: Optional[int] = None) -> None:
    """
    Sends a message to a Kafka topic.
    """
    try:
        if user_id is not None:
            message["user_id"] = user_id

        serialized_message = json.dumps(message).encode("utf-8")
        producer_instance = await get_kafka_producer()

        await producer_instance.send_and_wait(topic, serialized_message)
        logger.info(f"Message sent to Kafka topic '{topic}': {message}")

    except Exception as e:
        logger.error(f"Failed to send message to Kafka topic '{topic}': {e}")
        raise


async def shutdown_kafka_producer():
    global producer
    if producer:
        await producer.stop()
        logger.info("Kafka producer stopped.")
        producer = None
