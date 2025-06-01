from kafka import KafkaConsumer
from .kafka_producer import produce_result
from .agent_runner import run_agent
import json
import asyncio
import os
import time

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_IN = os.getenv("TOPIC_IN", "agent-tasks-inbound")


async def consume_kafka_messages():
    print("[Consumer] Starting Kafka consumer...", flush=True)
    loop = asyncio.get_event_loop()

    consumer = None
    for i in range(10):
        try:
            print(f"[Consumer] Attempt {i + 1}: Connecting to Kafka at {KAFKA_BROKER}...", flush=True)
            consumer = KafkaConsumer(
                TOPIC_IN,
                bootstrap_servers=[KAFKA_BROKER],
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                group_id="agent-service-group",
                auto_offset_reset="earliest",
                enable_auto_commit=True
            )
            print(f"[Consumer] Connected to Kafka at {KAFKA_BROKER}, topic='{TOPIC_IN}'", flush=True)
            break
        except Exception as e:
            print(f"[Consumer] Kafka not ready yet: {e}", flush=True)
            time.sleep(3)

    if consumer is None:
        print("[Consumer] Failed to connect to Kafka after 10 attempts. Exiting.", flush=True)
        return

    while True:
        for message in consumer:
            task = message.value
            print("[Agent Service] Received task:", task, flush=True)

            result = await loop.run_in_executor(None, run_agent, task)
            await loop.run_in_executor(None, produce_result, result)

        await asyncio.sleep(0.1)
