# Quick Start: Robotics

This guide walks through using Jumpstarter for robotics device testing. You
will set up a local exporter with serial, GPIO, and power control drivers to
automate testing of a robotics controller board.

## Prerequisites

Install the Jumpstarter CLI and the relevant drivers:

```console
$ pip install jumpstarter-cli jumpstarter-driver-pyserial jumpstarter-driver-power jumpstarter-driver-gpiod
```

## Exporter Configuration

Create an exporter configuration file (`exporter-robotics.yaml`) that exposes
serial, power, and GPIO interfaces to your robotics controller:

```yaml
apiVersion: jumpstarter.dev/v1alpha1
kind: ExporterConfig
metadata:
  name: robotics-controller
export:
  serial:
    type: jumpstarter_driver_pyserial.driver.PySerial
    config:
      url: "/dev/ttyUSB0"
      baudrate: 115200
  power:
    type: jumpstarter_driver_gpiod.driver.PowerSwitch
    config:
      device: "/dev/gpiochip0"
      line: 17
  gpio:
    type: jumpstarter_driver_gpiod.driver.DigitalOutput
    config:
      device: "/dev/gpiochip0"
      line: 18
```

## Starting a Session

Start a local exporter session:

```console
$ jmp shell --exporter exporter-robotics.yaml
```

## Interacting with the Device

Inside the Jumpstarter shell, use the CLI to control the robotics board:

```console
$ j power on
ok
$ echo "STATUS" | j serial pipe --no-output
$ j serial pipe
READY
^C
$ j power off
ok
```

Or use the Python API for programmatic control:

```python
import time
from jumpstarter.common.utils import env

with env() as client:
    client.power.on()
    time.sleep(2)

    serial = client.serial.open()
    serial.sendline("STATUS")
    serial.expect("READY")
    print(f"Board status: READY")

    client.power.off()
```

## Running Tests

Write a pytest test file (`test_robotics.py`) for automated board validation:

```python
import time
from jumpstarter_testing import JumpstarterTest
from jumpstarter_driver_gpiod.client import PinState

class TestRoboticsController(JumpstarterTest):
    def test_board_boots(self, client):
        client.power.on()
        time.sleep(5)
        serial = client.serial.open()
        serial.sendline("STATUS")
        serial.expect("READY")
        client.power.off()

    def test_gpio_output(self, client):
        client.gpio.on()
        value = client.gpio.read()
        assert value == PinState.ACTIVE
```

Run the tests:

```console
$ jmp shell --exporter exporter-robotics.yaml
$ pytest test_robotics.py
$ exit
```

## Related Drivers

- [PySerial](../../reference/package-apis/drivers/pyserial.md) - Serial port
  communication
- [Power](../../reference/package-apis/drivers/power.md) - Power control
- [gpiod](../../reference/package-apis/drivers/gpiod.md) - GPIO hardware control
- [Network](../../reference/package-apis/drivers/network.md) - Network
  interfaces
- [CAN](../../reference/package-apis/drivers/can.md) - Controller Area
  Network communication

## Next Steps

- Set up [distributed mode](setup-distributed-mode.md) to share robotics
  test hardware across your team
- Learn about [integration patterns](integration-patterns.md) for CI/CD
  pipelines with hardware-in-the-loop testing
- Explore [testing with pytest](pytest-usage.md) for structured test suites
