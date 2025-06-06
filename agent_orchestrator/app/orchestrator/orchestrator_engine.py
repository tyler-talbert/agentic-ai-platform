from ..kafka.producer import produce_task
from .task_model import AgentTask
from typing import Dict

task_store: Dict[str, AgentTask] = {}

class OrchestrationEngine:
    @staticmethod
    def handle_task(task_input: dict) -> AgentTask:
        task = AgentTask.create(type="GENERIC", input=task_input)
        task_store[task.id] = task
        produce_task(task)
        return task
