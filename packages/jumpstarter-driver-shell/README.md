# Shell driver

`jumpstarter-driver-shell` provides functionality for shell command execution.

## Installation

```bash
pip install jumpstarter-driver-shell
```

## Configuration

Example configuration:

```{literalinclude} shell.yaml
:language: yaml
```

```{doctest}
:hide:
>>> from jumpstarter.config import ExporterConfigV1Alpha1DriverInstance
>>> ExporterConfigV1Alpha1DriverInstance.from_path("source/api-reference/drivers/shell.yaml").instantiate()
Shell(...)
```

## API Reference

Assuming the exporter driver is configured as in the example above, the client methods will be generated dynamically, and they will be available as follows:

```{eval-rst}
.. autoclass:: jumpstarter_driver_shell.client.ShellClient
    :members:

.. function:: ls()
   :noindex:

   :returns: A tuple(stdout, stderr, return_code)

.. function:: method2()
    :noindex:

    :returns: A tuple(stdout, stderr, return_code)

.. function:: method3(arg1, arg2)
    :noindex:

    :returns: A tuple(stdout, stderr, return_code)

.. function:: env_var(arg1, arg2, ENV_VAR="value")
    :noindex:

    :returns: A tuple(stdout, stderr, return_code)
```
