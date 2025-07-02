try:
    import grpc
    from grpc import aio
    from grpc_reflection.v1alpha import reflection
    from proto import agent_pb2, agent_pb2_grpc
except Exception as e:  # pragma: no cover - optional runtime
    grpc = None
    aio = None
    reflection = None
    agent_pb2 = None
    agent_pb2_grpc = None
    _IMPORT_ERROR = e

import asyncio
from app.agent_runner.agent_runner import run_agent
from app.kafka_client.producer import produce_result


if agent_pb2_grpc:
    class _AgentServicer(agent_pb2_grpc.AgentServiceServicer):
        async def RunTask(self, request, context):
            if not request.task_id or not request.payload:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("task_id and payload required")
                return agent_pb2.TaskReply(status="FAILED", output="")

            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, run_agent, request.task_id, {"input": request.payload}
            )
            output = result.get("output", "")
            produce_result({"task_id": request.task_id, "output": output})

            return agent_pb2.TaskReply(status="COMPLETED", output=str(output))
else:
    _AgentServicer = None


async def serve(port: int = 50051):
    """Start the gRPC server if grpc is available."""
    if grpc is None or _AgentServicer is None:
        print(f"[gRPC] grpc unavailable: {_IMPORT_ERROR}", flush=True)
        return

    server = aio.server()
    agent_pb2_grpc.add_AgentServiceServicer_to_server(_AgentServicer(), server)

    if reflection is not None:
        service_names = (
            agent_pb2.DESCRIPTOR.services_by_name["AgentService"].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(service_names, server)
        print("[gRPC] Reflection enabled", flush=True)
    else:
        print("[gRPC] Reflection not available", flush=True)

    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    print(f"[gRPC] Server listening on {port}", flush=True)
    await server.wait_for_termination()