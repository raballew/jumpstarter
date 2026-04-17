import logging
import multiprocessing
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import mkdtemp
from uuid import UUID, uuid4

import grpc
from jumpstarter_protocol import jumpstarter_pb2, jumpstarter_pb2_grpc

from jumpstarter.common.exceptions import ConfigurationError
from jumpstarter.common.sandbox import SandboxPolicy

logger = logging.getLogger(__name__)


class _ChildProcessServicer(jumpstarter_pb2_grpc.ExporterServiceServicer):
    def __init__(self, driver_instance):
        self._driver = driver_instance

    def GetReport(self, request, context):
        return jumpstarter_pb2.GetReportResponse(
            reports=[
                instance.report(parent=parent, name=name)
                for (_, parent, name, instance) in self._driver.enumerate()
            ],
        )

    def DriverCall(self, request, context):
        return self._driver.DriverCall(request, context)

    def StreamingDriverCall(self, request, context):
        return self._driver.StreamingDriverCall(request, context)


def _child_process_entry(driver_class_path: str, driver_config: dict, socket_path: str, ready_event, success_flag):
    from concurrent import futures

    import grpc
    from jumpstarter_protocol import jumpstarter_pb2_grpc, router_pb2_grpc

    from jumpstarter.common.importlib import import_class

    try:
        driver_class = import_class(driver_class_path, [], True)
        driver_instance = driver_class(**driver_config)
        servicer = _ChildProcessServicer(driver_instance)

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
        jumpstarter_pb2_grpc.add_ExporterServiceServicer_to_server(servicer, server)
        router_pb2_grpc.add_RouterServiceServicer_to_server(driver_instance, server)
        server.add_insecure_port(f"unix://{socket_path}")
        server.start()

        success_flag.value = 1
        ready_event.set()

        server.wait_for_termination()
    except Exception:
        logger.exception("Child process failed for driver %s", driver_class_path)
        ready_event.set()


@dataclass
class ManagedProcess:
    process: multiprocessing.Process
    socket_path: str
    driver_class_path: str


class ProcessManager:
    def __init__(self):
        self._managed: list[ManagedProcess] = []
        self._temp_dirs: list[str] = []

    def spawn(self, driver_class_path: str, driver_config: dict, sandbox_policy: SandboxPolicy) -> ManagedProcess:
        temp_dir = mkdtemp(prefix="jumpstarter-sandbox-")
        self._temp_dirs.append(temp_dir)
        socket_path = str(Path(temp_dir) / "driver.sock")

        ready_event = multiprocessing.Event()
        success_flag = multiprocessing.Value("i", 0)

        process = multiprocessing.Process(
            target=_child_process_entry,
            args=(driver_class_path, driver_config, socket_path, ready_event, success_flag),
            daemon=True,
        )
        process.start()

        ready_event.wait(timeout=30)

        if success_flag.value != 1:
            process.join(timeout=5)
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise ConfigurationError(
                f"Driver process for '{driver_class_path}' failed to start (exit code: {process.exitcode})"
            )

        managed = ManagedProcess(
            process=process,
            socket_path=socket_path,
            driver_class_path=driver_class_path,
        )
        self._managed.append(managed)

        logger.info(
            "Spawned driver process pid=%d for %s on %s",
            process.pid,
            driver_class_path,
            socket_path,
        )

        return managed

    def _terminate_process(self, managed: ManagedProcess):
        if managed.process.is_alive():
            logger.info("Terminating driver process pid=%d", managed.process.pid)
            managed.process.terminate()
            managed.process.join(timeout=5)
            if managed.process.is_alive():
                logger.warning("Force killing driver process pid=%d", managed.process.pid)
                managed.process.kill()
                managed.process.join(timeout=2)

    def terminate(self, managed: ManagedProcess):
        self._terminate_process(managed)
        if managed in self._managed:
            self._managed.remove(managed)

    def close(self):
        for managed in self._managed:
            self._terminate_process(managed)
        self._managed.clear()

        for temp_dir in self._temp_dirs:
            shutil.rmtree(temp_dir, ignore_errors=True)
        self._temp_dirs.clear()

    def check_health(self) -> dict[str, bool]:
        return {
            f"{managed.driver_class_path}:{managed.process.pid}": managed.process.is_alive()
            for managed in self._managed
        }


@dataclass(kw_only=True)
class DriverProxy:
    socket_path: str
    driver_class_path: str
    children: dict = field(default_factory=dict)
    uuid: UUID = field(default_factory=uuid4)
    labels: dict = field(default_factory=dict)
    description: str | None = None
    client_class_path: str = "jumpstarter_driver_composite.client.CompositeClient"
    managed_process: ManagedProcess | None = None
    _manager: ProcessManager | None = None
    _channel: grpc.Channel | None = field(default=None, init=False, repr=False)
    _stub: jumpstarter_pb2_grpc.ExporterServiceStub | None = field(default=None, init=False, repr=False)

    def __post_init__(self):
        if self.managed_process is not None:
            self._channel = grpc.insecure_channel(f"unix://{self.socket_path}")
            self._stub = jumpstarter_pb2_grpc.ExporterServiceStub(self._channel)

    def client(self) -> str:
        return self.client_class_path

    def report(self, *, parent=None, name=None):
        return jumpstarter_pb2.DriverInstanceReport(
            uuid=str(self.uuid),
            parent_uuid=str(parent.uuid) if parent else None,
            labels=self.labels
            | {"jumpstarter.dev/client": self.client()}
            | ({"jumpstarter.dev/name": name} if name else {})
            | {"jumpstarter.dev/sandbox": "true"},
            description=self.description or None,
        )

    def enumerate(self, *, root=None, parent=None, name=None):
        if root is None:
            root = self
        return [(self.uuid, parent, name, self)]

    async def DriverCall(self, request, context):
        return self._stub.DriverCall(request)

    async def StreamingDriverCall(self, request, context):
        for response in self._stub.StreamingDriverCall(request):
            yield response

    async def GetReport(self, request, context):
        return self._stub.GetReport(request)

    def close(self):
        if self._channel is not None:
            self._channel.close()
            self._channel = None
            self._stub = None
        if self._manager is not None and self.managed_process is not None:
            self._manager.terminate(self.managed_process)
            self.managed_process = None

    def reset(self):
        pass

    def extra_labels(self) -> dict[str, str]:
        return {"jumpstarter.dev/sandbox": "true"}
