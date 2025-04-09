# CAN driver

`jumpstarter-driver-can` provides functionality for interacting with CAN bus connections, including support for ISO-TP (ISO 15765-2) protocol.

## Installation

```bash
pip install jumpstarter-driver-can
```

## Configuration

The driver provides several implementations that can be configured:

### Basic CAN

```yaml
type: "jumpstarter_driver_can.driver.Can"
config:
  channel: "can0"  # CAN channel to connect to
  interface: "socketcan"  # CAN interface to use
```

### ISO-TP Python Implementation

```yaml
type: "jumpstarter_driver_can.driver.IsoTpPython"
config:
  channel: "can0"  # CAN channel to connect to
  interface: "socketcan"  # CAN interface to use
  address:
    # Configure ISO-TP addressing
    addressing_mode: 1  # Normal addressing mode
    txid: 0x123  # Transmit ID
    rxid: 0x456  # Receive ID
  params:
    # Optional ISO-TP parameters
    stmin: 0
    blocksize: 8
    tx_data_length: 8
```

### ISO-TP Linux Socket Implementation (kernel 5.10+)

```yaml
type: "jumpstarter_driver_can.driver.IsoTpSocket"
config:
  channel: "can0"  # CAN channel to connect to
  address:
    # Configure ISO-TP addressing
    addressing_mode: 1  # Normal addressing mode
    txid: 0x123  # Transmit ID
    rxid: 0x456  # Receive ID
```

```{doctest}
:hide:
>>> from jumpstarter.config import ExporterConfigV1Alpha1DriverInstance
>>> import unittest.mock
>>> with unittest.mock.patch('can.Bus'):  # Mock can.Bus to avoid actual hardware connection
...     driver_config = ExporterConfigV1Alpha1DriverInstance.from_path("source/api-reference/drivers/can.yaml")
...     driver = driver_config.instantiate()
...     print(driver.__class__.__name__)
Can
```

## API Reference

### CAN Client

```{eval-rst}
.. autoclass:: jumpstarter_driver_can.client.CanClient()
    :members:
```

### ISO-TP Client

```{eval-rst}
.. autoclass:: jumpstarter_driver_can.client.IsoTpClient()
    :members:
```
