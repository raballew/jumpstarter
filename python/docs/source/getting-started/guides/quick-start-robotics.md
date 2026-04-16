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
    type: jumpstarter_driver_power.driver.PowerRelay
    config:
      gpio_chip: "/dev/gpiochip0"
      gpio_line: 17
  gpio:
    type: jumpstarter_driver_gpiod.driver.Gpiod
    config:
      chip: "/dev/gpiochip0"
      lines: [18, 19, 20, 21]
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
$ j serial write "STATUS\n"
$ j serial read
READY
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

    client.serial.write(b"STATUS\n")
    response = client.serial.read(1024)
    print(f"Board status: {response.decode()}")

    client.power.off()
```

## Running Tests

Write a pytest test file (`test_robotics.py`) for automated board validation:

```python
import time
from jumpstarter_testing import JumpstarterTest

class TestRoboticsController(JumpstarterTest):
    def test_board_boots(self):
        self.client.power.on()
        time.sleep(5)
        self.client.serial.write(b"STATUS\n")
        response = self.client.serial.read(1024)
        assert b"READY" in response
        self.client.power.off()

    def test_gpio_output(self):
        self.client.gpio.set_value(18, 1)
        value = self.client.gpio.get_value(18)
        assert value == 1
```

Run the tests:

```console
$ jmp shell --exporter exporter-robotics.yaml
$ pytest test_robotics.py
$ exit
```

## Related Drivers

- [PySerial](../../reference/package-apis/drivers/pyserial.md) -- Serial port
  communication
- [Power](../../reference/package-apis/drivers/power.md) -- Power control
- [gpiod](../../reference/package-apis/drivers/gpiod.md) -- GPIO hardware control
- [Network](../../reference/package-apis/drivers/network.md) -- Network
  interfaces
- [CAN](../../reference/package-apis/drivers/can.md) -- Controller Area
  Network communication

## Next Steps

- Set up [distributed mode](setup-distributed-mode.md) to share robotics
  test hardware across your team
- Learn about [integration patterns](integration-patterns.md) for CI/CD
  pipelines with hardware-in-the-loop testing
- Explore [testing with pytest](pytest-usage.md) for structured test suites
