import os
import signal

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

        health = manager.check_health()
        assert health[driver_class_path] is True

        os.kill(managed.process.pid, signal.SIGKILL)
        managed.process.join(timeout=5)

        health = manager.check_health()
        assert health[driver_class_path] is False

        manager.close()


class TestDriverProxy:
    def test_proxy_has_report_with_correct_client(self):
        from jumpstarter.exporter.process_manager import DriverProxy

        proxy = DriverProxy(
            socket_path="/tmp/fake.sock",
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
        )

        report = proxy.report()
        assert "jumpstarter.dev/client" in report.labels

    def test_proxy_report_includes_sandbox_label(self):
        from jumpstarter.exporter.process_manager import DriverProxy

        proxy = DriverProxy(
            socket_path="/tmp/fake.sock",
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
        )

        report = proxy.report()
        assert report.labels["jumpstarter.dev/sandbox"] == "true"

    def test_proxy_close_is_safe_without_process(self):
        from jumpstarter.exporter.process_manager import DriverProxy

        proxy = DriverProxy(
            socket_path="/tmp/fake.sock",
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
        )

        proxy.close()

    def test_proxy_enumerate_returns_self(self):
        from jumpstarter.exporter.process_manager import DriverProxy

        proxy = DriverProxy(
            socket_path="/tmp/fake.sock",
            driver_class_path="jumpstarter_driver_composite.driver.Composite",
        )

        entries = proxy.enumerate()
        assert len(entries) == 1
        assert entries[0][3] is proxy
