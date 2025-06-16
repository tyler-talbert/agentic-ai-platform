import logging, asyncio, json
from fastapi import Request

from app.kafka.producer import produce_task
from app.orchestrator.task_model import AgentTask
from app.orchestrator.task_store import TASK_STORE

log = logging.getLogger(__name__)


def _to_str(val) -> str:
    return val if isinstance(val, str) else json.dumps(
        val, ensure_ascii=False, separators=(",", ":")
    )


async def _background_embed_question(task_id: str, text: str, app: Request):
    """Embeds and upserts a *question* vector using the new dual-upsert flow."""
    try:
        text_str = _to_str(text)
        log.info(f"[Embedding] (bg) Embedding QUESTION for task {task_id}")
        await embed_and_upsert(task_id, text_str, is_answer=False, app=app)
        log.info(f"[Pinecone] (bg) Upserted QUESTION vector for task {task_id}")
    except Exception as e:
        log.exception(f"[Pinecone] (bg) Failed to upsert question {task_id}: {e}")


class OrchestrationEngine:
    @staticmethod
    async def handle_task(task_input: dict, request: Request) -> AgentTask:
        """
        Create an AgentTask, enqueue to Kafka, and embed the question text.
        `request` gives us app.state for the embed_upsert helper.
        """
        task = AgentTask.create(type="GENERIC", input=task_input)
        TASK_STORE[task.id] = task
        log.info(f"[Orchestrator] Created task with ID: {task.id}")

        produce_task(task)
        log.info("[Orchestrator] Produced task to Kafka.")

        text_to_embed = task_input.get("input", "")
        if text_to_embed:
            asyncio.create_task(
                _background_embed_question(task.id, text_to_embed, request)
            )

        return task
