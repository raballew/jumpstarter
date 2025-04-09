# QEMU driver

`jumpstarter-driver-qemu` provides functionality for interacting with QEMU virtualization platform.

## Installation

```bash
pip install jumpstarter-driver-qemu
```

## Configuration

Example configuration:

```{literalinclude} qemu.yaml
:language: yaml
```

```{doctest}
:hide:
>>> from jumpstarter.config import ExporterConfigV1Alpha1DriverInstance
>>> ExporterConfigV1Alpha1DriverInstance.from_path("source/api-reference/drivers/qemu.yaml").instantiate()
QEMUDriver(...)
```

## API Reference

Add API documentation here.
