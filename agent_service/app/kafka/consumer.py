import os
import json
import time
import asyncio
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable


def blocking_consume_loop():
    topic = os.getenv("TOPIC_IN", "agent-tasks-inbound")
    broker = os.getenv("KAFKA_BROKER", "kafka:9092")

    print(f"[Kafka Consumer] Attempting to connect to Kafka at {broker} and subscribe to topic '{topic}'")

    # Retry loop for waiting on Kafka to be ready
    for attempt in range(10):  # 10 tries, 2s apart = ~20 seconds
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=broker,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='agent-service-group',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            print("[Kafka Consumer] Connected to Kafka successfully.")
            break
        except NoBrokersAvailable:
            print(f"[Kafka Consumer] Kafka not available, retrying... ({attempt + 1}/10)")
            time.sleep(2)
    else:
        print("[Kafka Consumer] Failed to connect to Kafka after 10 attempts.")
        raise RuntimeError("Kafka was not available after retries")

    from app.agent_runner import run_agent
    from app.kafka.producer import produce_result

    for message in consumer:
        task_data = message.value
        task_id = task_data.get("id") or "unknown"
        result = run_agent(task_id, task_data.get("input", {}))
        produce_result(result)


async def consume_kafka_messages():
    print("[Consumer] Starting Kafka consumer (in background thread)...", flush=True)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, blocking_consume_loop)
