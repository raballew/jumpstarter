# CAN driver

`jumpstarter-driver-can` provides functionality for interacting with CAN bus connections.

## Installation

```bash
pip install jumpstarter-driver-can
```

## Configuration

Example configuration:

```{literalinclude} can.yaml
:language: yaml
```

```{doctest}
:hide:
>>> from jumpstarter.config import ExporterConfigV1Alpha1DriverInstance
>>> ExporterConfigV1Alpha1DriverInstance.from_path("source/api-reference/drivers/can.yaml").instantiate()
CANDriver(...)
```

## API Reference

```{eval-rst}
.. autoclass:: jumpstarter_driver_can.client.CanClient()
    :members:
```

```{eval-rst}
.. autoclass:: jumpstarter_driver_can.client.IsoTpClient()
    :members:
```
