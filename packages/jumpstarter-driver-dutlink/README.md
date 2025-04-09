# DUT Link driver

`jumpstarter-driver-dutlink` provides functionality for interacting with DUT Link devices.

## Installation

```bash
pip install jumpstarter-driver-dutlink
```

## Configuration

Example configuration:

```{literalinclude} dutlink.yaml
:language: yaml
```

```{doctest}
:hide:
>>> from jumpstarter.config import ExporterConfigV1Alpha1DriverInstance
>>> ExporterConfigV1Alpha1DriverInstance.from_path("source/api-reference/drivers/dutlink.yaml").instantiate()
DUTLinkDriver(...)
```

## API Reference

Add API documentation here.
