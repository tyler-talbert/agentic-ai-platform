import grpc
from . import agent_pb2 as agent__pb2

class AgentServiceStub(object):
    def __init__(self, channel):
        self.RunTask = channel.unary_unary(
            '/agent.AgentService/RunTask',
            request_serializer=agent__pb2.TaskRequest.SerializeToString,
            response_deserializer=agent__pb2.TaskReply.FromString,
        )

class AgentServiceServicer(object):
    def RunTask(self, request, context):
        raise NotImplementedError('Method not implemented!')


def add_AgentServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'RunTask': grpc.unary_unary_rpc_method_handler(
            servicer.RunTask,
            request_deserializer=agent__pb2.TaskRequest.FromString,
            response_serializer=agent__pb2.TaskReply.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'agent.AgentService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))