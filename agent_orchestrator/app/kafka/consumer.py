import os, json, time, asyncio, logging
from typing import Any

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from app.vector_db.embedder   import embed_text
from app.vector_db.vector_db  import get_index
from app.orchestrator.task_store import TASK_STORE

log = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_OUT    = os.getenv("TOPIC_OUT",    "agent-tasks-completed")
INDEX_NAME   = os.getenv("PINECONE_INDEX_NAME", "agent-knowledge-base")


def _json_compact(obj: Any) -> str:
    """Dict/list -> compact JSON string (no whitespace)."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def _extract_text(payload: Any) -> str:
    """
    Take whatever the agent put in `output` and return *just* the text
    that a language model should embed.

    Rules (checked in this order):
      1. If payload is a **str** -> return it.
      2. If payload is a **dict** AND payload["output"] is str -> return that.
      3. If payload is a **dict** with "results" list  -> join with new‑lines.
      4. Fallback → compact JSON (still embeddable, but noisy).
    """
    if isinstance(payload, str):
        return payload.strip()

    if isinstance(payload, dict):
        inner = payload.get("output")
        if isinstance(inner, str):
            return inner.strip()

        if isinstance(inner, dict) and isinstance(inner.get("results"), list):
            return "\n".join(map(str, inner["results"])).strip()

    return _json_compact(payload)



def blocking_result_consume_loop(task_store):
    log.info(f"[Kafka Consumer] Connecting to Kafka at {KAFKA_BROKER}, "
             f"topic '{TOPIC_OUT}'")


    for attempt in range(10):
        try:
            consumer = KafkaConsumer(
                TOPIC_OUT,
                bootstrap_servers=KAFKA_BROKER,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id="orchestrator-service-group",
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            )
            log.info("[Kafka Consumer] Connected successfully.")
            break
        except NoBrokersAvailable:
            log.warning(f"[Kafka Consumer] Kafka not available "
                        f"(attempt {attempt+1}/10); retrying…")
            time.sleep(2)
    else:
        raise RuntimeError("Kafka broker not available after retries")

    from app.orchestrator.task_model import AgentTask

    for msg in consumer:
        log.info(f"[Kafka Consumer] Received message: {msg.value}")

        task_id    = msg.value.get("task_id")
        raw_output = msg.value.get("output")
        text       = _extract_text(raw_output)

        task = task_store.get(task_id)
        if task:
            task.mark_completed(raw_output)
            log.info(f"[Task Store] Updated task {task_id} as COMPLETED.")
        else:
            log.warning(f"[Task Store] No task found with ID: {task_id}")

        try:
            embedding = asyncio.run(embed_text(text))
            index = get_index(INDEX_NAME)

            index.upsert(
                vectors=[{
                    "id": f"{task_id}-a",
                    "values": embedding,
                    "metadata": {
                        "type":    "answer",
                        "task_id": task_id,
                        "text":    text,
                    },
                }]
            )
            log.info(f"[Pinecone] Upserted answer vector for task {task_id}")

        except Exception as e:
            log.exception(f"[Pinecone] Failed to upsert answer vector "
                          f"for task {task_id}: {e}")


async def consume_kafka_results():
    log.info("[Consumer] Starting background Kafka consumer for completed tasks…")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, blocking_result_consume_loop, TASK_STORE)
