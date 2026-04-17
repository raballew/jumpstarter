import multiprocessing
import os
import signal
from unittest.mock import MagicMock, patch

import pytest

from jumpstarter.common.exceptions import ConfigurationError
from jumpstarter.common.sandbox import SandboxPolicy


class TestProcessManagerSpawn:
    def test_spawn_creates_child_process(self):
        from jumpstarter.exporter.process_manager import ProcessManager

        manager = ProcessManager()

        driver_class_path = "jumpstarter_driver_composite.driver.Composite"
        driver_config = {}
        sandbox_policy = SandboxPolicy(enabled=True)

        managed = manager.spawn(driver_class_path, driver_config, sandbox_policy)

        assert managed.process.is_alive()
        assert managed.process.pid != os.getpid()
        assert managed.socket_path != ""

        manager.close()

    def test_spawn_raises_on_child_startup_failure(self):
        from jumpstarter.exporter.process_manager import ProcessManager

        manager = ProcessManager()

        sandbox_policy = SandboxPolicy(enabled=True)

        with pytest.raises(ConfigurationError):
            manager.spawn("nonexistent.module.NoSuchDriver", {}, sandbox_policy)

        manager.close()

    def test_spawn_error_includes_child_exception_message(self):
        from jumpstarter.exporter.process_manager import ProcessManager

        manager = ProcessManager()
        sandbox_policy = SandboxPolicy(enabled=True)

        with pytest.raises(ConfigurationError) as exc_info:
            manager.spawn("nonexistent.module.NoSuchDriver", {}, sandbox_policy)

        error_message = str(exc_info.value)
        assert "No module named" in error_message, (
            f"Expected child exception details in parent error, got: {error_message}"
        )

        manager.close()

    def test_spawn_cleans_temp_dir_on_child_startup_failure(self):
        from pathlib import Path

        from jumpstarter.exporter.process_manager import ProcessManager

        manager = ProcessManager()
        sandbox_policy = SandboxPolicy(enabled=True)

        with pytest.raises(ConfigurationError):
            manager.spawn("nonexistent.module.NoSuchDriver", {}, sandbox_policy)

        for temp_dir in manager._temp_dirs:
            assert not Path(temp_dir).exists(), f"temp dir {temp_dir} was not cleaned up after spawn failure"

        assert len(manager._temp_dirs) == 0

        manager.close()

    def test_spawn_creates_unique_socket_per_driver(self):
        from jumpstarter.exporter.process_manager import ProcessManager

        manager = ProcessManager()

        driver_class_path = "jumpstarter_driver_composite.driver.Composite"
        sandbox_policy = SandboxPolicy(enabled=True)

        managed1 = manager.spawn(driver_class_path, {}, sandbox_policy)
        managed2 = manager.spawn(driver_class_path, {}, sandbox_policy)

        assert managed1.socket_path != managed2.socket_path
        assert managed1.process.pid != managed2.process.pid

        manager.close()


class TestProcessManagerSocketPathValidation:
    def test_spawn_raises_when_socket_path_exceeds_unix_limit(self):
        from unittest.mock import patch

        from jumpstarter.exporter.process_manager import ProcessManager

        manager = ProcessManager()
        sandbox_policy = SandboxPolicy(enabled=True)

        long_prefix = "/tmp/" + "a" * 200 + "/"
        with patch("jumpstarter.exporter.process_manager.mkdtemp", return_value=long_prefix):
            with pytest.raises(ConfigurationError, match="socket path exceeds"):
                manager.spawn("jumpstarter_driver_composite.driver.Composite", {}, sandbox_policy)

        manager.close()


class TestProcessManagerClose:
    def test_close_terminates_all_child_processes(self):
        from jumpstarter.exporter.process_manager import ProcessManager

        manager = ProcessManager()

        driver_class_path = "jumpstarter_driver_composite.driver.Composite"
        sandbox_policy = SandboxPolicy(enabled=True)

        managed1 = manager.spawn(driver_class_path, {}, sandbox_policy)
        managed2 = manager.spawn(driver_class_path, {}, sandbox_policy)

        manager.close()

        managed1.process.join(timeout=5)
        managed2.process.join(timeout=5)
        assert not managed1.process.is_alive()
        assert not managed2.process.is_alive()

    def test_close_is_idempotent(self):
        from jumpstarter.exporter.process_manager import ProcessManager

        manager = ProcessManager()

        driver_class_path = "jumpstarter_driver_composite.driver.Composite"
        sandbox_policy = SandboxPolicy(enabled=True)

        manager.spawn(driver_class_path, {}, sandbox_policy)

        manager.close()
        manager.close()


class TestProcessManagerCrashDetection:
    def test_is_alive_returns_false_after_process_killed(self):
        from jumpstarter.exporter.process_manager import ProcessManager

        manager = ProcessManager()

        driver_class_path = "jumpstarter_driver_composite.driver.Composite"
        sandbox_policy = SandboxPolicy(enabled=True)

        managed = manager.spawn(driver_class_path, {}, sandbox_policy)

        assert managed.process.is_alive()

        os.kill(managed.process.pid, signal.SIGKILL)
        managed.process.join(timeout=5)

        assert not managed.process.is_alive()

        manager.close()

    def test_check_health_reports_dead_process(self):
        from jumpstarter.exporter.process_manager import ProcessManager

        manager = ProcessManager()

        driver_class_path = "jumpstarter_driver_composite.driver.Composite"
        sandbox_policy = SandboxPolicy(enabled=True)

        managed = manager.spawn(driver_class_path, {}, sandbox_policy)
        health_key = f"{driver_class_path}:{managed.process.pid}"

        health = manager.check_health()
        assert health[health_key] is True

        os.kill(managed.process.pid, signal.SIGKILL)
        managed.process.join(timeout=5)

        health = manager.check_health()
        assert health[health_key] is False

        manager.close()

    def test_check_health_distinguishes_processes_with_same_class_path(self):
        from jumpstarter.exporter.process_manager import ProcessManager

        manager = ProcessManager()

        driver_class_path = "jumpstarter_driver_composite.driver.Composite"
        sandbox_policy = SandboxPolicy(enabled=True)

        managed1 = manager.spawn(driver_class_path, {}, sandbox_policy)
        manager.spawn(driver_class_path, {}, sandbox_policy)

        os.kill(managed1.process.pid, signal.SIGKILL)
        managed1.process.join(timeout=5)

        health = manager.check_health()
        alive_count = sum(1 for alive in health.values() if alive)
        dead_count = sum(1 for alive in health.values() if not alive)

        assert alive_count == 1
        assert dead_count == 1

        manager.close()


class TestDriverProxyConformsToDriverLike:
    def test_proxy_instance_satisfies_driver_like_protocol(self):
        from jumpstarter.common.driver_protocol import DriverLike
        from jumpstarter.exporter.process_manager import DriverProxy

        proxy = DriverProxy(
            socket_path="/tmp/fake.sock",
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
        )

        assert isinstance(proxy, DriverLike)

    def test_proxy_method_signatures_match_driver_like_protocol(self):
        import inspect

        from jumpstarter.common.driver_protocol import DriverLike
        from jumpstarter.exporter.process_manager import DriverProxy

        protocol_hints = {
            name: inspect.signature(method)
            for name, method in inspect.getmembers(DriverLike, predicate=inspect.isfunction)
            if not name.startswith("_")
        }

        for method_name, protocol_sig in protocol_hints.items():
            proxy_method = getattr(DriverProxy, method_name)
            proxy_sig = inspect.signature(proxy_method)
            assert proxy_sig.parameters.keys() == protocol_sig.parameters.keys(), (
                f"DriverProxy.{method_name} parameters {list(proxy_sig.parameters.keys())} "
                f"do not match DriverLike.{method_name} {list(protocol_sig.parameters.keys())}"
            )


class TestDriverProxy:
    def test_proxy_has_report_with_correct_client(self):
        from jumpstarter.exporter.process_manager import DriverProxy

        proxy = DriverProxy(
            socket_path="/tmp/fake.sock",
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
            client_class_path="jumpstarter_driver_composite.client.CompositeClient",
        )

        report = proxy.report()
        assert "jumpstarter.dev/client" in report.labels

    def test_proxy_client_uses_provided_class_path(self):
        from jumpstarter.exporter.process_manager import DriverProxy

        proxy = DriverProxy(
            socket_path="/tmp/fake.sock",
            driver_class_path="some_driver.driver.MyDriver",
            client_class_path="some_driver.client.MyClient",
        )

        assert proxy.client() == "some_driver.client.MyClient"

    def test_proxy_report_includes_sandbox_label(self):
        from jumpstarter.exporter.process_manager import DriverProxy

        proxy = DriverProxy(
            socket_path="/tmp/fake.sock",
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
        )

        report = proxy.report()
        assert report.labels["jumpstarter.dev/sandbox"] == "true"

    def test_proxy_close_is_safe_without_manager(self):
        from jumpstarter.exporter.process_manager import DriverProxy

        proxy = DriverProxy(
            socket_path="/tmp/fake.sock",
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
        )

        proxy.close()

    def test_proxy_close_terminates_child_process(self):
        from jumpstarter.exporter.process_manager import DriverProxy, ProcessManager

        manager = ProcessManager()
        sandbox_policy = SandboxPolicy(enabled=True)
        managed = manager.spawn("jumpstarter_driver_composite.driver.Composite", {}, sandbox_policy)

        proxy = DriverProxy(
            socket_path=managed.socket_path,
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
            managed_process=managed,
            _manager=manager,
        )

        assert managed.process.is_alive()

        proxy.close()

        managed.process.join(timeout=5)
        assert not managed.process.is_alive()

    def test_proxy_close_is_idempotent_with_managed_process(self):
        from jumpstarter.exporter.process_manager import DriverProxy, ProcessManager

        manager = ProcessManager()
        sandbox_policy = SandboxPolicy(enabled=True)
        managed = manager.spawn("jumpstarter_driver_composite.driver.Composite", {}, sandbox_policy)

        proxy = DriverProxy(
            socket_path=managed.socket_path,
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
            managed_process=managed,
            _manager=manager,
        )

        proxy.close()
        proxy.close()

    def test_proxy_does_not_implement_stream(self):
        from jumpstarter.exporter.process_manager import DriverProxy

        proxy = DriverProxy(
            socket_path="/tmp/fake.sock",
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
        )

        assert not hasattr(proxy, "Stream"), (
            "DriverProxy must not implement Stream - "
            "the child process handles streaming natively via RouterServiceServicer"
        )

    def test_proxy_enumerate_returns_self(self):
        from jumpstarter.exporter.process_manager import DriverProxy

        proxy = DriverProxy(
            socket_path="/tmp/fake.sock",
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
        )

        entries = proxy.enumerate()
        assert len(entries) == 1
        assert entries[0][3] is proxy


class TestChildProcessEntryServerCleanup:
    def test_server_stopped_when_wait_for_termination_raises(self):
        import grpc as grpc_module

        from jumpstarter.exporter.process_manager import _child_process_entry

        mock_server = MagicMock()
        mock_server.wait_for_termination.side_effect = RuntimeError("unexpected termination")

        ready_event = multiprocessing.Event()
        success_flag = multiprocessing.Value("i", 0)
        error_buffer = multiprocessing.Array("c", 4096)

        original_grpc_server = grpc_module.server
        try:
            grpc_module.server = MagicMock(return_value=mock_server)
            with patch("jumpstarter.common.importlib.import_class", return_value=MagicMock()):
                _child_process_entry(
                    "fake.module.FakeDriver",
                    {},
                    "/tmp/fake.sock",
                    ready_event,
                    success_flag,
                    error_buffer,
                )
        finally:
            grpc_module.server = original_grpc_server

        mock_server.stop.assert_called_once_with(grace=0)
