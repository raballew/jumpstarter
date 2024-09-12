import os
from dataclasses import dataclass, field
from uuid import uuid4

import grpc
import pytest
from anyio import Event, create_memory_object_stream
from anyio.abc import AnyByteStream
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

from jumpstarter.streams import RouterStream, forward_stream
from jumpstarter.v1 import (
    jumpstarter_pb2,
    jumpstarter_pb2_grpc,
    router_pb2_grpc,
)


@dataclass(kw_only=True)
class MockRouter(router_pb2_grpc.RouterServiceServicer):
    pending: dict[str, AnyByteStream] = field(default_factory=dict)

    async def Stream(self, _request_iterator, context):
        event = Event()
        context.add_done_callback(lambda _: event.set())
        authorization = dict(list(context.invocation_metadata()))["authorization"]
        async with RouterStream(context=context) as stream:
            if authorization in self.pending:
                async with forward_stream(stream, self.pending[authorization]):
                    await event.wait()
            else:
                self.pending[authorization] = stream
                await event.wait()
                del self.pending[authorization]


@dataclass(kw_only=True)
class MockController(jumpstarter_pb2_grpc.ControllerServiceServicer):
    router_endpoint: str
    queue: (MemoryObjectSendStream[str], MemoryObjectReceiveStream[str]) = field(
        init=False, default_factory=lambda: create_memory_object_stream[str](32)
    )

    async def Register(self, request, context):
        return jumpstarter_pb2.RegisterResponse(uuid=str(uuid4()))

    async def Unregister(self, request, context):
        return jumpstarter_pb2.UnregisterResponse()

    async def RequestLease(self, request, context):
        return jumpstarter_pb2.RequestLeaseResponse(name=str(uuid4()))

    async def GetLease(self, request, context):
        return jumpstarter_pb2.GetLeaseResponse(exporter_uuid=str(uuid4()))

    async def ReleaseLease(self, request, context):
        return jumpstarter_pb2.ReleaseLeaseResponse()

    async def Dial(self, request, context):
        token = str(uuid4())
        await self.queue[0].send(token)
        return jumpstarter_pb2.DialResponse(router_endpoint=self.router_endpoint, router_token=token)

    async def Listen(self, request, context):
        async for token in self.queue[1]:
            yield jumpstarter_pb2.ListenResponse(router_endpoint=self.router_endpoint, router_token=token)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def mock_controller():
    server = grpc.aio.server()
    port = server.add_insecure_port("127.0.0.1:0")

    controller = MockController(router_endpoint=f"127.0.0.1:{port}")
    router = MockRouter()

    jumpstarter_pb2_grpc.add_ControllerServiceServicer_to_server(controller, server)
    router_pb2_grpc.add_RouterServiceServicer_to_server(router, server)

    await server.start()

    yield f"127.0.0.1:{port}"

    await server.stop(grace=None)


os.environ["TQDM_DISABLE"] = "1"
