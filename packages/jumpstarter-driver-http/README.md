# HTTP driver

`jumpstarter-driver-http` provides functionality for HTTP communication.

## Installation

```bash
pip install jumpstarter-driver-http
```

## Configuration

Example configuration:

```{literalinclude} http.yaml
:language: yaml
```

```{doctest}
:hide:
>>> from jumpstarter.config import ExporterConfigV1Alpha1DriverInstance
>>> ExporterConfigV1Alpha1DriverInstance.from_path("source/api-reference/drivers/http.yaml").instantiate()
HTTPDriver(...)
```

## API Reference

Add API documentation here.
