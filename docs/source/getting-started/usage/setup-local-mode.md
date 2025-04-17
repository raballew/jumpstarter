# Setup Local Mode

This guide shows you how to use Jumpstarter with a local exporter (client and
exporter running on the same host).

## Prerequisites

Install these packages in your Python environment:

- `jumpstarter-cli` - The Jumpstarter CLI for interacting with exporters
- `jumpstarter-driver-opendal` - The OpenDAL storage driver for file operations
- `jumpstarter-driver-power` - The base power driver for managing power states

These driver packages include mock implementations, enabling you to test the
connection between an exporter and client without physical hardware.

## Create an Exporter Configuration

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

## Spawn an Exporter Shell

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
$ exit
```

When you run the `j` command in the exporter shell, you're accessing the CLI
interfaces exposed by the drivers configured in your exporter. In this example:

- `j power on` - Activates the power interface from the MockPower driver
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

#### Running a Python Script

Run a quick Python script directly from the command line:

```shell
$ jmp shell --exporter example
$ python - <<EOF
from jumpstarter.common.utils import env
with env() as client:
    print(client.power.on())
EOF
ok
$ exit
```

This example demonstrates using Python to interact with the exporter:

1. The `env()` function from `jumpstarter.common.utils` automatically connects
   to the exporter configured in your shell environment.

2. The `with env() as client:` statement creates a client connected to your
   local exporter and handles connection setup and cleanup.

3. `client.power.on()` directly calls the power driver's "on" method—the same
   action that `j power on` performs in the CLI.

This approach gives you programmatic access to all driver functions, allowing
you to create automated sequences and complex control logic beyond what's
possible with simple CLI commands.

#### Running a Python File

For more complex scenarios, create and run the follow `example.py` file:

```python
import time

from jumpstarter.common.utils import env

with env() as client:
    # Power on the device
    print("Power on")
    client.power.on()

    # Wait three seconds
    print("Waiting 3 seconds...")
    time.sleep(3.0)

    # Power off the device
    print("Power off")
    client.power.off()

    print("Done!")
```

```shell
$ jmp shell --exporter example
$ python ./example.py
$ exit
```

This example demonstrates a complete power cycle workflow using a Python file:

1. The script creates a sequence of operations (power on → wait → power off)
   that would be tedious to perform manually through the CLI.

2. Using a separate file allows you to:

   - Save and reuse complex sequences
   - Add logic, error handling, and conditional operations
   - Import other Python libraries (like `time` in this example)
   - Build more sophisticated automation scripts

3. When you run the script in the exporter shell, it has access to the same
   client environment as the interactive Python example, but with the advantages
   of using a persistent file.

This approach is ideal for test scripts, device initialization sequences, and
other multi-step operations that need to be repeated consistently.

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

3. Benefits of using `pytest`:

   - Organize tests into logical classes and methods
   - Generate test reports with success/failure statuses
   - Use `pytest`'s extensive features (parameterization, fixtures, etc.)
   - Run selective tests based on names or tags

This approach is ideal for creating test suites that verify your hardware
behaves correctly under different conditions, allowing for systematic testing
and validation.