import logging, asyncio, json
from app.kafka.producer import produce_task
from app.orchestrator.task_model import AgentTask
from app.orchestrator.task_store import TASK_STORE
from app.vector_db.embedder import embed_text

log = logging.getLogger(__name__)


def _to_str(val) -> str:
    return val if isinstance(val, str) else json.dumps(
        val, ensure_ascii=False, separators=(",", ":")
    )

async def _embed_and_upsert_question(task_id: str, text, vector_index):
    try:
        text_str = _to_str(text)
        log.info(f"[Embedding] (bg) Embedding question for task {task_id}")
        embedding = await embed_text(text_str)
        log.info(f"[Embedding] (bg) Received vector length={len(embedding)}")

        vector_index.upsert(
            vectors=[
                {
                    "id": f"{task_id}-q",
                    "values": embedding,
                    "metadata": {
                        "type": "question",
                        "task_id": task_id,
                        "text": text_str,
                    },
                }
            ]
        )
        log.info(f"[Pinecone] (bg) Upserted question vector for task {task_id}")
    except Exception as e:
        log.exception(
            f"[Pinecone] (bg) Failed to embed/upsert question for task {task_id}: {e}"
        )

class OrchestrationEngine:
    @staticmethod
    async def handle_task(task_input: dict, vector_index=None) -> AgentTask:
        task = AgentTask.create(type="GENERIC", input=task_input)
        TASK_STORE[task.id] = task
        log.info(f"[Orchestrator] Created task with ID: {task.id}")

        produce_task(task)
        log.info("[Orchestrator] Produced task to Kafka.")

        if vector_index:
            text_to_embed = task_input.get("input", "")
            if text_to_embed:
                asyncio.create_task(
                    _embed_and_upsert_question(task.id, text_to_embed, vector_index)
                )

        return task
