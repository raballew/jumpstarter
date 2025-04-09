# Corellium Driver

`jumpstarter-driver-corellium` provides functionality for interacting with [Corellium](https://corellium.com) virtualization platform.

## Installation

```bash
pip install jumpstarter-driver-corellium
```

## Configuration

Example configuration:

```{literalinclude} corellium.yaml
:language: yaml
```

```{doctest}
:hide:
>>> from jumpstarter.config import ExporterConfigV1Alpha1DriverInstance
>>> ExporterConfigV1Alpha1DriverInstance.from_path("source/api-reference/drivers/corellium.yaml").instantiate()
Corellium(...)
```

## API Reference

For more examples, check the [examples folder](./examples).

### ExporterConfig Example

You can run an exporter by running: `jmp exporter shell -c $file`:

```yaml
apiVersion: jumpstarter.dev/v1alpha1
kind: ExporterConfig
# endpoint and token are intentionally left empty
metadata:
  namespace: default
  name: corellium-demo
endpoint: ""
token: ""
export:
  rd1ae:
    type: jumpstarter_driver_corellium.driver.Corellium
    config:
      project_id: "778f00af-5e9b-40e6-8e7f-c4f14b632e9c"
      device_name: "jmp-rd1ae"
      device_flavor: "kronos"
```

```yaml
apiVersion: jumpstarter.dev/v1alpha1
kind: ExporterConfig
# endpoint and token are intentionally left empty
metadata:
  namespace: default
  name: corellium-demo
endpoint: ""
token: ""
export:
  rd1ae:
    type: jumpstarter_driver_corellium.driver.Corellium
    config:
      project_id: "778f00af-5e9b-40e6-8e7f-c4f14b632e9c"
      device_name: "jmp-rd1ae"
      device_flavor: "kronos"
      device_os: "1.0"
      device_build: "Critical Application Monitor (Baremetal)"
```
