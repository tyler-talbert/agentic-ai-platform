import os
import json
import time
import asyncio

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from app.vector_db.embedder import embed_text
from app.vector_db.vector_db import get_index  # unified vector_db

from app.orchestrator.task_store import TASK_STORE

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_OUT    = os.getenv("TOPIC_OUT",    "agent-tasks-completed")
INDEX_NAME   = os.getenv("PINECONE_INDEX_NAME", "agent-knowledge-base")

def blocking_result_consume_loop(task_store):
    print(f"[Kafka Consumer] Connecting to Kafka at {KAFKA_BROKER}, topic '{TOPIC_OUT}'")

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
            print(f"[Kafka Consumer] Kafka not available (attempt {attempt+1}/10), retrying...")
            time.sleep(2)
    else:
        raise RuntimeError("Kafka broker not available after retries")

    from app.orchestrator.task_model import AgentTask

    for message in consumer:
        print(f"[Kafka Consumer] Received message: {message.value}")
        task_id = message.value.get("task_id")
        output = message.value.get("output")

        task = task_store.get(task_id)
        if not task:
            print(f"[Task Store] No task found with ID: {task_id}")
            continue

        task.mark_completed(output)
        print(f"[Task Store] Updated task {task_id} as COMPLETED.")

        if output:
            try:

                embedding = asyncio.run(embed_text(output))

                index = get_index(INDEX_NAME)
                index.upsert(vectors=[{
                    "id": f"{task_id}-a",
                    "values": embedding,
                    "metadata": {
                        "type": "answer",
                        "task_id": task_id,
                        "text": output
                    }
                }])
                print(f"[Pinecone] Upserted answer vector for task {task_id}")
            except Exception as e:
                print(f"[Pinecone] Failed to upsert answer for task {task_id}: {e}")

async def consume_kafka_results():
    print("[Consumer] Starting background Kafka consumer for completed tasks...")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, blocking_result_consume_loop, TASK_STORE)
