# Quick Start: Edge AI

This guide walks through using Jumpstarter for edge AI appliance testing. You
will set up a local exporter with storage, network, and power drivers to
automate flashing, booting, and validating an edge AI device.

## Prerequisites

Install the Jumpstarter CLI and the relevant drivers:

```console
$ pip install jumpstarter-cli jumpstarter-driver-opendal jumpstarter-driver-network jumpstarter-driver-power jumpstarter-driver-pyserial jumpstarter-driver-gpiod jumpstarter-testing pytest
```

## Exporter Configuration

Create an exporter configuration file (`exporter-edge-ai.yaml`) that exposes
storage, network, serial, and power interfaces to your edge AI device:

```yaml
apiVersion: jumpstarter.dev/v1alpha1
kind: ExporterConfig
metadata:
  name: edge-ai-device
export:
  power:
    type: jumpstarter_driver_gpiod.driver.PowerSwitch
    config:
      device: "/dev/gpiochip0"
      line: 17
  serial:
    type: jumpstarter_driver_pyserial.driver.PySerial
    config:
      url: "/dev/ttyUSB0"
      baudrate: 115200
  storage:
    type: jumpstarter_driver_opendal.driver.Opendal
    config:
      scheme: "fs"
      kwargs:
        root: "/mnt/device-storage"
  network:
    type: jumpstarter_driver_network.driver.TcpNetwork
    config:
      host: "192.168.1.50"
      port: 8080
```

## Starting a Session

Start a local exporter session:

```console
$ jmp shell --exporter exporter-edge-ai.yaml
```

## Interacting with the Device

Inside the Jumpstarter shell, use the CLI and Python API to manage the device:

```console
$ j power on
ok
$ j storage write-from-path /device/firmware.img firmware.img
$ j power off
ok
```

Or use the Python API for a complete flash-and-test workflow:

```python
import time
from jumpstarter.common.utils import env

with env() as client:
    client.power.off()
    time.sleep(1)

    client.storage.write_from_path("/firmware/model-v2.img", "model-v2.img")

    client.power.on()
    time.sleep(10)

    serial = client.serial.open()
    serial.sendline("inference --model /opt/model.bin --input test.jpg")
    serial.expect("inference complete")
    print("Inference completed successfully")

    client.power.off()
```

## Running Tests

Write a pytest test file (`test_edge_ai.py`) for automated device validation:

```python
import time
from jumpstarter_testing import JumpstarterTest

class TestEdgeAIDevice(JumpstarterTest):
    def test_device_boots_after_flash(self, client):
        client.power.off()
        time.sleep(1)
        client.power.on()
        time.sleep(15)
        serial = client.serial.open()
        serial.sendline("uname -a")
        serial.expect("Linux")

    def test_inference_runtime_available(self, client):
        serial = client.serial.open()
        serial.sendline("which inference-engine")
        serial.expect("/usr/bin/inference-engine")
```

Run the tests:

```console
$ jmp shell --exporter exporter-edge-ai.yaml
$ pytest test_edge_ai.py
$ exit
```

## Related Drivers

- [OpenDAL](../../reference/package-apis/drivers/opendal.md) - Storage
  access layer
- [Flashers](../../reference/package-apis/drivers/flashers.md) - Flash memory
  programming
- [Network](../../reference/package-apis/drivers/network.md) - Network
  interfaces
- [Power](../../reference/package-apis/drivers/power.md) - Power control
- [PySerial](../../reference/package-apis/drivers/pyserial.md) - Serial
  console access
- [QEMU](../../reference/package-apis/drivers/qemu.md) - Virtual device
  testing

## Next Steps

- Set up [distributed mode](setup-distributed-mode.md) to share edge AI
  test hardware across your team
- Learn about [integration patterns](integration-patterns.md) for CI/CD
  pipelines
- Explore [testing with pytest](pytest-usage.md) for structured test suites
