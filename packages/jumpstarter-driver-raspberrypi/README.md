# Raspberry Pi driver

`jumpstarter-driver-raspberrypi` provides functionality for interacting with Raspberry Pi devices.

## Installation

```bash
pip install jumpstarter-driver-raspberrypi
```

## Configuration

Example configuration:

```{literalinclude} raspberrypi.yaml
:language: yaml
```

```{doctest}
:hide:
>>> from jumpstarter.config import ExporterConfigV1Alpha1DriverInstance
>>> ExporterConfigV1Alpha1DriverInstance.from_path("source/api-reference/drivers/raspberrypi.yaml").instantiate()
RaspberryPiDriver(...)
```

## API Reference

Add API documentation here.
