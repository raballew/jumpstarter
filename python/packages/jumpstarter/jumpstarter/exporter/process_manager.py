import logging
import multiprocessing
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import mkdtemp
from uuid import UUID, uuid4

from jumpstarter_protocol import jumpstarter_pb2

from jumpstarter.common.exceptions import ConfigurationError
from jumpstarter.common.sandbox import SandboxPolicy

logger = logging.getLogger(__name__)


def _child_process_entry(driver_class_path: str, driver_config: dict, socket_path: str, ready_event, success_flag):
    from concurrent import futures

    import grpc
    from jumpstarter_protocol import jumpstarter_pb2_grpc, router_pb2_grpc

    from jumpstarter.common.importlib import import_class

    try:
        driver_class = import_class(driver_class_path, [], True)
        driver_instance = driver_class(**driver_config)

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
        jumpstarter_pb2_grpc.add_ExporterServiceServicer_to_server(driver_instance, server)
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

    def close(self):
        for managed in self._managed:
            if managed.process.is_alive():
                logger.info("Terminating driver process pid=%d", managed.process.pid)
                managed.process.terminate()
                managed.process.join(timeout=5)
                if managed.process.is_alive():
                    logger.warning("Force killing driver process pid=%d", managed.process.pid)
                    managed.process.kill()
                    managed.process.join(timeout=2)
        self._managed.clear()

        for temp_dir in self._temp_dirs:
            shutil.rmtree(temp_dir, ignore_errors=True)
        self._temp_dirs.clear()

    def check_health(self) -> dict[str, bool]:
        return {managed.driver_class_path: managed.process.is_alive() for managed in self._managed}


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

    def close(self):
        if self._manager is not None:
            self._manager.close()
            self._manager = None

    def reset(self):
        pass

    def extra_labels(self) -> dict[str, str]:
        return {"jumpstarter.dev/sandbox": "true"}
