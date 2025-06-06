from ..kafka.producer import produce_task
from .task_model import AgentTask
from app.orchestrator.task_store import TASK_STORE

class OrchestrationEngine:
    @staticmethod
    def handle_task(task_input: dict) -> AgentTask:
        task = AgentTask.create(type="GENERIC", input=task_input)
        TASK_STORE[task.id] = task
        produce_task(task)
        return task
