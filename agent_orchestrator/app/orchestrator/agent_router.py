from fastapi import APIRouter, HTTPException, Request
import grpc
from proto import agent_pb2
from app.orchestrator.task_model import TaskStatus
from app.orchestrator.orchestrator_engine import OrchestrationEngine
from app.orchestrator.task_store import TASK_STORE

router = APIRouter(prefix="/v1")

@router.post("/tasks")
async def create_task(task_input: dict, request: Request):
    try:
        vector_index = getattr(request.app.state, "vector_index", None)
        task = await OrchestrationEngine.handle_task(task_input, vector_index)

        stub = getattr(request.app.state, "grpc_stub", None)
        if stub:
            req = agent_pb2.TaskRequest(task_id=task.id, payload=task_input.get("input", ""))
            try:
                resp = await stub.RunTask(req, timeout=15.0)
                if resp.status != "COMPLETED":
                    raise grpc.RpcError("unexpected status")
            except Exception:
                print("[Orchestrator] gRPC call failed, continuing as PENDING", flush=True)

        return {"task_id": task.id, "status": task.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = TASK_STORE.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
