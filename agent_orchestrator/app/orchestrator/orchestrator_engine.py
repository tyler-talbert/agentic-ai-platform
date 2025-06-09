from app.kafka.producer import produce_task
from app.orchestrator.task_model import AgentTask
from app.orchestrator.task_store import TASK_STORE
from app.vector_db.embedding_service import embed_text
import uuid

class OrchestrationEngine:
    @staticmethod
    async def handle_task(task_input: dict, vector_index=None) -> AgentTask:
        task = AgentTask.create(type="GENERIC", input=task_input)
        TASK_STORE[task.id] = task
        produce_task(task)

        if vector_index:
            text_to_embed = task_input.get("input", "")
            if text_to_embed:
                embedding = await embed_text(text_to_embed)
                vector_index.upsert(vectors=[{
                    "id": str(uuid.uuid4()),
                    "values": embedding,
                    "metadata": {
                        "task_id": task.id,
                        "input": text_to_embed
                    }
                }])

        return task

