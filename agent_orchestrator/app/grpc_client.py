import os

GRPC_TARGET = os.getenv("AGENT_GRPC_URL", "agent_service:50051")

async def run_task(task_id: str, payload: str):
    try:
        import grpc
        from proto import agent_pb2, agent_pb2_grpc
    except Exception as e:
        print(f"[gRPC] grpc unavailable: {e}", flush=True)
        return None

    async with grpc.aio.insecure_channel(GRPC_TARGET) as channel:
        stub = agent_pb2_grpc.AgentServiceStub(channel)
        request = agent_pb2.TaskRequest(task_id=task_id, payload=payload)
        return await stub.RunTask(request)