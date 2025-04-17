# Setup Local Mode

This guide shows you how to use Jumpstarter with a client and exporter running
on the same host.

## Prerequisites

Install these packages in your Python environment:

- `jumpstarter-cli` - The Jumpstarter CLI for interacting with exporters
- `jumpstarter-driver-opendal` - The OpenDAL storage driver for file operations
- `jumpstarter-driver-power` - The base power driver for managing power states

These driver packages include mock implementations, enabling you to test the
connection between an exporter and client without physical hardware.

## Instructions

### Create an Exporter Configuration

Create an exporter configuration to define the capabilities of your local test
exporter. This configuration mirrors a regular exporter config but leaves the
`endpoint` and `token` fields empty since you don't need to connect to the
controller service.

Create `example.yaml` in `/etc/jumpstarter/exporters` with this content:

```yaml
apiVersion: jumpstarter.dev/v1alpha1
kind: ExporterConfig
metadata:
  namespace: default
  name: example
endpoint: ""
token: ""
export:
  storage:
    type: jumpstarter_driver_opendal.driver.MockStorageMux
  power:
    type: jumpstarter_driver_power.driver.MockPower
```

### Spawn an Exporter Shell

Interact with your local exporter using the "exporter shell" functionality in
the `jmp` CLI. When you spawn a shell, Jumpstarter runs a local exporter
instance in the background for the duration of your shell session.

```shell
$ jmp shell --exporter example
```

### Exiting the Exporter Shell

To terminate the local exporter, simply exit the shell:

```shell
$ exit
```

### Interact with the Exporter Shell

The exporter shell provides access to driver CLI interfaces through the magic
`j` command:

```shell
$ jmp shell --exporter example
$ j
Usage: j [OPTIONS] COMMAND [ARGS]...

  Generic composite device

Options:
  --help  Show this message and exit.

Commands:
  power    Generic power
  storage  Generic storage mux
$ j power on
ok
$ j power off
ok
$ exit
```

When you run the `j` command in the exporter shell, you're accessing the CLI
interfaces exposed by the drivers configured in your exporter. In this example:

- `j power` - Would access the power interface from the MockPower driver
- `j storage` - Would access the storage interface from the MockStorageMux
  driver

Each driver can expose different commands through this interface, making it easy
to interact with the mock hardware. The command structure follows `j
<driver_type> <action>`, where available actions depend on the specific driver.

### Use the Python API in a Shell

The exporter shell exposes the local exporter via environment variables,
enabling you to run any Python code that interacts with the client/exporter.
This approach works especially well for complex operations or when a driver
doesn't provide a CLI.

#### Using Python with Jumpstarter

Create a Python file for interacting with your exporter. This example
(`example.py`) demonstrates a complete power cycle workflow:

```python
import time
from jumpstarter.common.utils import env

with env() as client:
    client.power.on()
    client.power.off()
```

```shell
$ jmp shell --exporter example
$ python ./example.py
$ exit
```

This example demonstrates how Python interacts with the exporter:

1. The `env()` function from `jumpstarter.common.utils` automatically connects
   to the exporter configured in your shell environment.

2. The `with env() as client:` statement creates a client connected to your
   local exporter and handles connection setup and cleanup.

3. `client.power.on()` directly calls the power driver's "on" method—the same
   action that `j power on` performs in the CLI.

4. `client.power.off()` directly calls the power driver's "off" method—the same
   action that `j power off` performs in the CLI.

Using a Python with Jumpstarter allows you to:

   - Create sequences of operations (power on → wait → power off)
   - Save and reuse complex workflows
   - Add logic, error handling, and conditional operations
   - Import other Python libraries (like `time` in this example)
   - Build sophisticated automation scripts

#### Running `pytest` in the Shell

For multiple test cases, run a `pytest` suite using Jumpstarter's built-in
testing library:

```python
# mytest.py
from jumpstarter_testing.pytest import JumpstarterTest

class MyTest(JumpstarterTest):
    def test_power_on(self, client):
        client.power.on()

    def test_power_off(self, client):
        client.power.off()
```

```shell
$ jmp shell --exporter example
$ pytest ./mytest.py
$ exit
```

This example demonstrates using `pytest` for structured testing with
Jumpstarter:

1. The `JumpstarterTest` is a `pytest` fixture that:

   - Automatically establishes a connection to your exporter
   - Provides a pre-configured `client` object to each test method
   - Handles setup and teardown between tests

2. Each test method receives the `client` parameter, giving access to all driver
   interfaces just like in the previous examples.

Benefits of using `pytest` with Jumpstarter are:

   - Organize tests into logical classes and methods
   - Generate test reports with success/failure statuses
   - Use `pytest`'s extensive features (parameterization, fixtures, etc.)
   - Run selective tests based on names or tags