from fastapi import APIRouter, HTTPException, Request
from app.orchestrator.orchestrator_engine import OrchestrationEngine
from app.orchestrator.task_store import TASK_STORE

router = APIRouter(prefix="/v1")

@router.post("/tasks")
async def create_task(task_input: dict, request: Request):
    try:
        vector_index = getattr(request.app.state, "vector_index", None)
        task = await OrchestrationEngine.handle_task(task_input, vector_index)
        return {"task_id": task.id, "status": task.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = TASK_STORE.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
