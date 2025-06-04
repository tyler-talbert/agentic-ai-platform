from ..kafka.producer import produce_task
from .task_model import AgentTask

class OrchestrationEngine:
    @staticmethod
    def handle_task(task_input: dict) -> AgentTask:
        task = AgentTask.create(type="GENERIC", input=task_input)
        produce_task(task)
        return task
