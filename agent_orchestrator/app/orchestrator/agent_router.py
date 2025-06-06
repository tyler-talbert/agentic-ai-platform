from fastapi import APIRouter, HTTPException
from ..orchestrator.orchestrator_engine import OrchestrationEngine, task_store
from ..orchestrator.task_model import AgentTask

router = APIRouter(prefix="/v1")

@router.post("/tasks")
async def create_task(task_input: dict):
    try:
        task = OrchestrationEngine.handle_task(task_input)
        return {"task_id": task.id, "status": task.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
