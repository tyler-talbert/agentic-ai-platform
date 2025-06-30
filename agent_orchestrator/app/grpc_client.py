import os
from typing import Optional

GRPC_TARGET = os.getenv("AGENT_GRPC_URL", "agent_service:50051")

_STUB: Optional[object] = None

async def init_stub():
    global _STUB
    if _STUB is not None:
        return _STUB
    import grpc
    from proto import agent_pb2_grpc
    channel = grpc.aio.insecure_channel(GRPC_TARGET)
    _STUB = agent_pb2_grpc.AgentServiceStub(channel)
    return _STUB

async def run_task(task_id: str, payload: str):
    try:
        import grpc
        from proto import agent_pb2
        stub = await init_stub()
    except Exception as e:
        print(f"[gRPC] grpc unavailable: {e}", flush=True)
        return None

    request = agent_pb2.TaskRequest(task_id=task_id, payload=payload)
    return await stub.RunTask(request)