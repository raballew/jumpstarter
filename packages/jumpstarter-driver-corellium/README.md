# Corellium Driver

`jumpstarter-driver-corellium` provides functionality for interacting with [Corellium](https://corellium.com) virtualization platform.

## Installation

```bash
pip install jumpstarter-driver-corellium
```

## Configuration

The driver requires Corellium API credentials to be set as environment variables:
- `CORELLIUM_API_HOST`: The Corellium API host URL
- `CORELLIUM_API_TOKEN`: Your Corellium API authentication token

Example configuration:

```{literalinclude} corellium.yaml
:language: yaml
```

```{doctest}
:hide:
>>> from jumpstarter.config import ExporterConfigV1Alpha1DriverInstance
>>> import unittest.mock
>>> import os
>>> # Mock environment variables required by Corellium driver
>>> with unittest.mock.patch.dict(os.environ, {
...     'CORELLIUM_API_HOST': 'https://example.com',
...     'CORELLIUM_API_TOKEN': 'mock_token'
... }):
...     driver_config = ExporterConfigV1Alpha1DriverInstance.from_path("source/api-reference/drivers/corellium.yaml")
...     driver = driver_config.instantiate()
...     print(driver.__class__.__name__)
Corellium
```

## API Reference

### Corellium Client

```{eval-rst}
.. autoclass:: jumpstarter_driver_corellium.client.CorelliumClient()
    :members:
```