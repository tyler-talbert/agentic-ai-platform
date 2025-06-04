from fastapi import APIRouter, HTTPException
from ..orchestrator.orchestrator_engine import OrchestrationEngine
from ..orchestrator.task_model import AgentTask

router = APIRouter()

@router.post("/tasks")
async def create_task(task_input: dict):
    try:
        task = OrchestrationEngine.handle_task(task_input)
        return {"task_id": task.id, "status": task.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
