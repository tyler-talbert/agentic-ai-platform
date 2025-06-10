import logging

from app.kafka.producer import produce_task
from app.orchestrator.task_model import AgentTask
from app.orchestrator.task_store import TASK_STORE
from app.vector_db.embedder import embed_text

log = logging.getLogger(__name__)

class OrchestrationEngine:
    @staticmethod
    async def handle_task(task_input: dict, vector_index=None) -> AgentTask:
        task = AgentTask.create(type="GENERIC", input=task_input)
        TASK_STORE[task.id] = task
        log.info(f"[Orchestrator] Created task with ID: {task.id}")

        produce_task(task)
        log.info(f"[Orchestrator] Produced task to Kafka.")

        if vector_index:
            text_to_embed = task_input.get("input", "")
            if text_to_embed:
                try:
                    log.info(f"[Embedding] Embedding question for task {task.id}")
                    embedding = await embed_text(text_to_embed)
                    log.info(f"[Embedding] Received vector of length {len(embedding)}")

                    vector_index.upsert(vectors=[{
                        "id": f"{task.id}-q",
                        "values": embedding,
                        "metadata": {
                            "type": "question",
                            "task_id": task.id,
                            "text": text_to_embed
                        }
                    }])
                    log.info(f"[Pinecone] Upserted question vector for task {task.id}")
                except Exception:
                    log.exception(f"[Pinecone] Failed to embed/upsert question for task {task.id}")

        return task
