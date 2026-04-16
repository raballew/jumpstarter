# Quick Start: Automotive

This guide walks through using Jumpstarter for automotive ECU diagnostics
testing. You will set up a local exporter with a UDS (Unified Diagnostic
Services) over DoIP (Diagnostics over Internet Protocol) driver and run a
diagnostic workflow against a simulated ECU.

## Prerequisites

Install the Jumpstarter CLI and the automotive diagnostics drivers:

```console
$ pip install jumpstarter-cli jumpstarter-driver-uds-doip
```

## Exporter Configuration

Create an exporter configuration file (`exporter-automotive.yaml`) that
exposes a UDS over DoIP interface to your ECU:

```yaml
apiVersion: jumpstarter.dev/v1alpha1
kind: ExporterConfig
metadata:
  name: automotive-ecu
export:
  uds:
    type: jumpstarter_driver_uds_doip.driver.UdsDoip
    config:
      ecu_ip: "192.168.1.100"
      ecu_logical_address: 224
      request_timeout: 5
```

For local development without real hardware, use the mock ECU from the
`jumpstarter-example-automotive` package (see `python/examples/automotive/`).

## Starting a Session

Start a local exporter session:

```console
$ jmp shell --exporter exporter-automotive.yaml
```

## Running Diagnostics

Inside the Jumpstarter shell, use the Python API to interact with the ECU:

```python
from jumpstarter.common.utils import env

with env() as client:
    did_values = client.uds.read_data_by_identifier([0xF190])
    print(f"VIN: {did_values[0].value}")
```

## Running Tests

Write a pytest test file (`test_ecu.py`) for automated ECU validation:

```python
from jumpstarter_testing import JumpstarterTest

class TestEcuDiagnostics(JumpstarterTest):
    def test_read_vin(self, client):
        did_values = client.uds.read_data_by_identifier([0xF190])
        assert len(did_values) == 1

    def test_session_transition(self, client):
        client.uds.change_session("extended")
```

Run the tests:

```console
$ jmp shell --exporter exporter-automotive.yaml
$ pytest test_ecu.py
$ exit
```

## Related Drivers

- [UDS over DoIP](../../reference/package-apis/drivers/uds-doip.md) - UDS
  diagnostics over Ethernet
- [UDS over CAN](../../reference/package-apis/drivers/uds-can.md) - UDS
  diagnostics over CAN bus
- [DoIP](../../reference/package-apis/drivers/doip.md) - Raw DoIP protocol
- [SOME/IP](../../reference/package-apis/drivers/someip.md) - SOME/IP
  service-oriented communication
- [XCP](../../reference/package-apis/drivers/xcp.md) - Measurement and
  calibration protocol

## Next Steps

- Explore the [automotive example](https://github.com/jumpstarter-dev/jumpstarter/tree/main/python/examples/automotive)
  for a complete ECU diagnostic test suite with a stateful mock ECU
- Set up [distributed mode](setup-distributed-mode.md) to share ECU test
  hardware across your team
- Learn about [integration patterns](integration-patterns.md) for CI/CD
  pipelines
