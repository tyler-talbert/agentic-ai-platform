import json
import time
import os
from kafka import KafkaProducer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

def init_kafka_producer():
    for attempt in range(10):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            print(f"[Kafka] Connected to broker at {KAFKA_BROKER}", flush=True)
            return producer
        except Exception as e:
            print(f"[Kafka] Attempt {attempt + 1} failed: {e}", flush=True)
            time.sleep(3)
    raise RuntimeError("Kafka unavailable after retries")
