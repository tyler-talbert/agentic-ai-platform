from kafka import KafkaConsumer
from .kafka_producer import produce_result
from .agent_runner import run_agent
import json
import asyncio
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC_IN = os.getenv("TOPIC_IN", "agent-tasks-inbound")

async def consume_kafka_messages():
    loop = asyncio.get_event_loop()
    consumer = KafkaConsumer(
        TOPIC_IN,
        bootstrap_servers=[KAFKA_BROKER],
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        group_id="agent-service-group",
        auto_offset_reset="earliest",
        enable_auto_commit=True
    )

    print(f"Kafka Consumer connected to broker {KAFKA_BROKER}, listening on topic '{TOPIC_IN}'")

    while True:
        for message in consumer:
            task = message.value
            print("[Agent Service] Received task:", task)

            result = await loop.run_in_executor(None, run_agent, task)
            await loop.run_in_executor(None, produce_result, result)

        await asyncio.sleep(0.1)
