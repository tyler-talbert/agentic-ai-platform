from app.logger import setup_logger
import json
import time
import os
from kafka import KafkaProducer, errors
from ..orchestrator.task_model import AgentTask

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_IN     = os.getenv("TOPIC_IN",    "agent-tasks-inbound")

producer = None
log = setup_logger()

MAX_SEND_RETRIES = 5


def init_kafka_producer():
    global producer
    for attempt in range(10):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            log.info(f"[Kafka] Connected to broker at {KAFKA_BROKER}")
            return producer
        except Exception as e:
            log.info(f"[Kafka] Attempt {attempt + 1} failed: {e}")
            time.sleep(3)
    raise RuntimeError("Kafka unavailable after retries")


def _ensure_producer():
    global producer
    if producer is None:
        producer = init_kafka_producer()


def produce_task(task: AgentTask):
    global producer
    _ensure_producer()

    for attempt in range(1, MAX_SEND_RETRIES + 1):
        try:
            producer.send(TOPIC_IN, task.dict())
            log.info(f"[Kafka] Task {task.id} sent to {TOPIC_IN}")
            return
        except (errors.NoBrokersAvailable, errors.KafkaTimeoutError) as e:
            log.warning(
                f"[Kafka] send attempt {attempt}/{MAX_SEND_RETRIES} failed: {e}"
            )
            time.sleep(2)
            try:
                producer.close(5)
            except Exception:
                pass
            producer = None            # refresh metadata on next loop
            _ensure_producer()

    raise RuntimeError(
        f"Kafka still unavailable after {MAX_SEND_RETRIES} retries"
    )
