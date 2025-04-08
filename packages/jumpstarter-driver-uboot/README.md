# U-Boot driver

`jumpstarter-driver-uboot` provides functionality for interacting with the U-Boot bootloader. This driver does not interact with the DUT directly, instead it should be configured with backing power and serial drivers.

## Installation

```bash
pip install jumpstarter-driver-uboot
```

## Configuration

Example configuration:

```yaml
type: "jumpstarter_driver_uboot.driver.UbootConsole"
children:
  power:
    type: "jumpstarter_driver_power.driver.MockPower"
    config: {} # omitted, power driver configuration
  serial:
    type: "jumpstarter_driver_pyserial.driver.PySerial"
    config: # omitted, serial driver configuration
      url: "loop://"
      # instead of configuring the power and serial driver inline
      # other drivers configured on the exporter can also be referenced
      # power:
      #   ref: "dutlink.power"
      # serial:
      #   ref: "dutlink.console"
config:
  prompt: "=>" # the u-boot command prompt to expect, defaults to "=>"
```

```{doctest}
:hide:
>>> from jumpstarter.config import ExporterConfigV1Alpha1DriverInstance
>>> ExporterConfigV1Alpha1DriverInstance.from_path("source/api-reference/drivers/uboot.yaml").instantiate()
UbootConsole(...)
```

## API Reference

```{eval-rst}
.. autoclass:: jumpstarter_driver_uboot.client.UbootConsoleClient()
    :members:
```
