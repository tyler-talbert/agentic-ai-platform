from app.logger import setup_logger
import json
import time
import os
from kafka import KafkaProducer
from ..orchestrator.task_model import AgentTask

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_IN = os.getenv("TOPIC_IN", "agent-tasks-inbound")

producer = None
log = setup_logger()

def init_kafka_producer():
    global producer
    for attempt in range(10):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            log.info(f"[Kafka] Connected to broker at {KAFKA_BROKER}")
            return producer
        except Exception as e:
            log.info(f"[Kafka] Attempt {attempt + 1} failed: {e}")
            time.sleep(3)
    raise RuntimeError("Kafka unavailable after retries")

def produce_task(task: AgentTask):
    if producer is None:
        raise RuntimeError("Kafka producer not initialized.")
    producer.send(TOPIC_IN, task.dict())
    log.info(f"[Kafka] Task {task.id} sent to {TOPIC_IN}")
