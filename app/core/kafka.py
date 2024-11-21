import json
import logging
from typing import Optional
from confluent_kafka import Producer
from app.core.config import settings

logger = logging.getLogger("kafka")

producer_config = {
    "bootstrap.servers": settings.kafka_broker,
}

producer = Producer(producer_config)


def produce_message(topic: str, message: dict, user_id: Optional[int] = None) -> None:
    """
    Sends a message to a Kafka topic.
    """
    try:
        if user_id is not None:
            message["user_id"] = user_id

        serialized_message = json.dumps(message).encode("utf-8")

        producer.produce(topic, serialized_message)
        producer.flush()
        logger.info(f"Message sent to Kafka topic '{topic}': {message}")
    except Exception as e:
        logger.error(f"Failed to send message to Kafka topic '{topic}': {e}")
        raise
