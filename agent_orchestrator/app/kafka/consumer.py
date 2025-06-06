import os
import json
import time
import asyncio
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_OUT = os.getenv("TOPIC_OUT", "agent-tasks-completed")

def blocking_result_consume_loop():
    print(f"[Kafka Consumer] Connecting to broker at {KAFKA_BROKER} to listen on '{TOPIC_OUT}'")

    for attempt in range(10):
        try:
            consumer = KafkaConsumer(
                TOPIC_OUT,
                bootstrap_servers=KAFKA_BROKER,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='orchestrator-service-group',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            print("[Kafka Consumer] Connected successfully.")
            break
        except NoBrokersAvailable:
            print(f"[Kafka Consumer] Kafka not available (attempt {attempt + 1}/10). Retrying...")
            time.sleep(2)
    else:
        raise RuntimeError("Kafka broker not available after retries")

    from app.orchestrator.orchestrator_engine import update_task_with_result

    for message in consumer:
        print(f"[Kafka Consumer] Received completed task: {message.value}")
        update_task_with_result(message.value)

async def consume_kafka_results():
    print("[Consumer] Starting background Kafka consumer for completed tasks...")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, blocking_result_consume_loop)
