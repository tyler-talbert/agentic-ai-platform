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


class OrchestrationEngine:
    @staticmethod
    async def handle_task(task_input: dict, request: Request) -> AgentTask:
        """
        Create an AgentTask and push it to Kafka.
        Question embedding is deferred to agent_service; orchestrator no
        longer imports embed_and_upsert.
        """
        task = AgentTask.create(type="GENERIC", input=task_input)
        TASK_STORE[task.id] = task
        log.info(f"[Orchestrator] Created task with ID: {task.id}")

        produce_task(task)
        log.info("[Orchestrator] Produced task to Kafka.")

        text_to_embed = task_input.get("input", "")
        if text_to_embed:
            log.info(
                f"[Orchestrator] Question text for task {task.id}: "
                f"{_to_str(text_to_embed)[:80]}…"
            )

        return task
