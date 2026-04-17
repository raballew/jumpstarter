import os
import signal

import pytest

from jumpstarter.common.exceptions import ConfigurationError


@pytest.fixture
def process_manager():
    from jumpstarter.exporter.process_manager import ProcessManager

    manager = ProcessManager()
    yield manager
    manager.close()


class TestProcessManagerSpawn:
    def test_spawn_creates_child_process(self, process_manager):
        driver_class_path = "jumpstarter_driver_composite.driver.Composite"
        driver_config = {}

        managed = process_manager.spawn(driver_class_path, driver_config)

        assert managed.process.is_alive()
        assert managed.process.pid != os.getpid()
        assert managed.socket_path != ""

    def test_spawn_raises_on_child_startup_failure(self, process_manager):
        with pytest.raises(ConfigurationError):
            process_manager.spawn("nonexistent.module.NoSuchDriver", {})

    def test_spawn_cleans_temp_dir_on_failure(self, process_manager):
        from pathlib import Path

        with pytest.raises(ConfigurationError):
            process_manager.spawn("nonexistent.module.NoSuchDriver", {})

        for temp_dir in process_manager._temp_dirs:
            assert not Path(temp_dir).exists()

    def test_spawn_creates_unique_socket_per_driver(self, process_manager):
        driver_class_path = "jumpstarter_driver_composite.driver.Composite"

        managed1 = process_manager.spawn(driver_class_path, {})
        managed2 = process_manager.spawn(driver_class_path, {})

        assert managed1.socket_path != managed2.socket_path
        assert managed1.process.pid != managed2.process.pid


class TestProcessManagerClose:
    def test_close_terminates_all_child_processes(self, process_manager):
        driver_class_path = "jumpstarter_driver_composite.driver.Composite"

        managed1 = process_manager.spawn(driver_class_path, {})
        managed2 = process_manager.spawn(driver_class_path, {})

        process_manager.close()

        managed1.process.join(timeout=5)
        managed2.process.join(timeout=5)
        assert not managed1.process.is_alive()
        assert not managed2.process.is_alive()

    def test_close_is_idempotent(self, process_manager):
        driver_class_path = "jumpstarter_driver_composite.driver.Composite"

        process_manager.spawn(driver_class_path, {})

        process_manager.close()
        process_manager.close()


class TestProcessManagerCrashDetection:
    def test_is_alive_returns_false_after_process_killed(self, process_manager):
        driver_class_path = "jumpstarter_driver_composite.driver.Composite"

        managed = process_manager.spawn(driver_class_path, {})

        assert managed.process.is_alive()

        os.kill(managed.process.pid, signal.SIGKILL)
        managed.process.join(timeout=5)

        assert not managed.process.is_alive()

    def test_check_health_reports_dead_process(self, process_manager):
        driver_class_path = "jumpstarter_driver_composite.driver.Composite"

        managed = process_manager.spawn(driver_class_path, {})
        health_key = f"{driver_class_path}:{managed.process.pid}"

        health = process_manager.check_health()
        assert health[health_key] is True

        os.kill(managed.process.pid, signal.SIGKILL)
        managed.process.join(timeout=5)

        health = process_manager.check_health()
        assert health[health_key] is False

    def test_check_health_distinguishes_processes_with_same_class_path(self, process_manager):
        driver_class_path = "jumpstarter_driver_composite.driver.Composite"

        managed1 = process_manager.spawn(driver_class_path, {})
        process_manager.spawn(driver_class_path, {})

        os.kill(managed1.process.pid, signal.SIGKILL)
        managed1.process.join(timeout=5)

        health = process_manager.check_health()
        alive_count = sum(1 for alive in health.values() if alive)
        dead_count = sum(1 for alive in health.values() if not alive)

        assert alive_count == 1
        assert dead_count == 1


class TestDriverProxyConformsToDriverLike:
    def test_proxy_instance_satisfies_driver_like_protocol(self):
        from jumpstarter.common.driver_protocol import DriverLike
        from jumpstarter.exporter.process_manager import DriverProxy

        proxy = DriverProxy(
            socket_path="/tmp/fake.sock",
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
        )

        assert isinstance(proxy, DriverLike)

    def test_driver_instance_satisfies_driver_like_protocol(self):
        from jumpstarter_driver_composite.driver import Composite

        from jumpstarter.common.driver_protocol import DriverLike

        driver = Composite()

        assert isinstance(driver, DriverLike)


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

    def test_proxy_close_terminates_child_process(self, process_manager):
        from jumpstarter.exporter.process_manager import DriverProxy

        managed = process_manager.spawn("jumpstarter_driver_composite.driver.Composite", {})

        proxy = DriverProxy(
            socket_path=managed.socket_path,
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
            managed_process=managed,
            _manager=process_manager,
        )

        assert managed.process.is_alive()

        proxy.close()

        managed.process.join(timeout=5)
        assert not managed.process.is_alive()

    def test_proxy_enumerate_returns_self(self):
        from jumpstarter.exporter.process_manager import DriverProxy

        proxy = DriverProxy(
            socket_path="/tmp/fake.sock",
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
        )

        entries = proxy.enumerate()
        assert len(entries) == 1
        assert entries[0][3] is proxy


class TestDriverProxyGrpcForwarding:
    def test_proxy_channel_is_lazy_initialized(self, process_manager):
        from jumpstarter.exporter.process_manager import DriverProxy

        managed = process_manager.spawn("jumpstarter_driver_composite.driver.Composite", {})

        proxy = DriverProxy(
            socket_path=managed.socket_path,
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
            managed_process=managed,
            _manager=process_manager,
        )

        assert proxy._channel is None
        assert proxy._stub is None

    def test_proxy_get_report_via_grpc(self, process_manager):
        import grpc
        from google.protobuf.empty_pb2 import Empty
        from jumpstarter_protocol import jumpstarter_pb2_grpc

        managed = process_manager.spawn("jumpstarter_driver_composite.driver.Composite", {})

        channel = grpc.insecure_channel(f"unix://{managed.socket_path}")
        stub = jumpstarter_pb2_grpc.ExporterServiceStub(channel)

        response = stub.GetReport(Empty())
        assert response.reports is not None
        assert len(response.reports) > 0

        channel.close()

    def test_proxy_forwards_get_report_through_stub(self, process_manager):
        import asyncio

        from google.protobuf.empty_pb2 import Empty

        from jumpstarter.exporter.process_manager import DriverProxy

        managed = process_manager.spawn("jumpstarter_driver_composite.driver.Composite", {})

        proxy = DriverProxy(
            socket_path=managed.socket_path,
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
            managed_process=managed,
            _manager=process_manager,
        )

        async def _test():
            response = await proxy.GetReport(Empty(), None)
            assert response.reports is not None
            assert len(response.reports) > 0
            proxy.close()

        asyncio.run(_test())

    def test_proxy_forwards_driver_call_through_proxy_method(self, process_manager):
        import asyncio

        import grpc
        from jumpstarter_protocol import jumpstarter_pb2

        from jumpstarter.exporter.process_manager import DriverProxy

        managed = process_manager.spawn("jumpstarter_driver_composite.driver.Composite", {})

        proxy = DriverProxy(
            socket_path=managed.socket_path,
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
            managed_process=managed,
            _manager=process_manager,
        )

        request = jumpstarter_pb2.DriverCallRequest(
            uuid=str(managed.driver_class_path),
            method="nonexistent_method",
        )

        async def _test():
            with pytest.raises(grpc.RpcError) as exc_info:
                await proxy.DriverCall(request, None)
            assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
            proxy.close()

        asyncio.run(_test())

    def test_proxy_uses_async_channel(self, process_manager):
        import asyncio

        import grpc.aio
        from google.protobuf.empty_pb2 import Empty

        from jumpstarter.exporter.process_manager import DriverProxy

        managed = process_manager.spawn("jumpstarter_driver_composite.driver.Composite", {})

        proxy = DriverProxy(
            socket_path=managed.socket_path,
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
            managed_process=managed,
            _manager=process_manager,
        )

        async def _test():
            await proxy.GetReport(Empty(), None)
            assert isinstance(proxy._channel, grpc.aio.Channel)
            proxy.close()

        asyncio.run(_test())

    def test_proxy_close_then_manager_close_is_safe(self, process_manager):
        from jumpstarter.exporter.process_manager import DriverProxy

        managed = process_manager.spawn("jumpstarter_driver_composite.driver.Composite", {})

        proxy = DriverProxy(
            socket_path=managed.socket_path,
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
            managed_process=managed,
            _manager=process_manager,
        )

        proxy.close()
