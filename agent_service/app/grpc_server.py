try:
    import grpc
    from grpc import aio
    from proto import agent_pb2, agent_pb2_grpc
except Exception as e:  # pragma: no cover - optional runtime
    grpc = None
    aio = None
    agent_pb2 = None
    agent_pb2_grpc = None
    _IMPORT_ERROR = e

from app.agent_runner.agent_runner import run_agent


if agent_pb2_grpc:
    class _AgentServicer(agent_pb2_grpc.AgentServiceServicer):
        async def RunTask(self, request, context):
            result = run_agent(request.task_id, {"input": request.payload})
            return agent_pb2.TaskReply(
                status=result.get("status", ""),
                output=str(result.get("output", "")),
            )
else:
    _AgentServicer = None


async def serve(port: int = 50051):
    """Start the gRPC server if grpc is available."""
    if grpc is None or _AgentServicer is None:
        print(f"[gRPC] grpc unavailable: {_IMPORT_ERROR}", flush=True)
        return

    server = aio.server()
    agent_pb2_grpc.add_AgentServiceServicer_to_server(_AgentServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    print(f"[gRPC] Server listening on {port}", flush=True)
    await server.wait_for_termination()