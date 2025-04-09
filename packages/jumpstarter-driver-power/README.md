# Power driver

`jumpstarter-driver-power` provides functionality for interacting with power control devices.

## Installation

```bash
pip install jumpstarter-driver-power
```

## Configuration

Example configuration:

```{literalinclude} power.yaml
:language: yaml
```

```{doctest}
:hide:
>>> from jumpstarter.config import ExporterConfigV1Alpha1DriverInstance
>>> ExporterConfigV1Alpha1DriverInstance.from_path("source/api-reference/drivers/power.yaml").instantiate()
PowerDriver(...)
```

## API Reference

Add API documentation here.
