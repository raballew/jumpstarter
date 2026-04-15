import os
import signal
import subprocess
import time
from dataclasses import dataclass, field
from typing import AsyncGenerator

import anyio
from anyio import EndOfStream

from jumpstarter.driver import Driver, export

BLOCKED_ENV_VARS: set[str] = {
    "LD_PRELOAD",
    "LD_LIBRARY_PATH",
    "PATH",
    "PYTHONPATH",
    "BASH_ENV",
    "KUBECONFIG",
    "HOME",
}

BLOCKED_ENV_PREFIXES: tuple[str, ...] = (
    "LD_",
    "BASH_FUNC_",
)


@dataclass(kw_only=True)
class Shell(Driver):
    """shell driver for Jumpstarter"""

    methods: dict[str, str | dict[str, str | int]]
    shell: list[str] = field(default_factory=lambda: ["bash", "-c"])
    timeout: int = 300
    cwd: str | None = None

    def __post_init__(self):
        super().__post_init__()
        for method_name, method_config in self.methods.items():
            if isinstance(method_config, dict) and "description" in method_config:
                self.methods_description[method_name] = method_config["description"]

    def _get_method_command(self, method: str) -> str:
        """Extract the command string from a method configuration"""
        method_config = self.methods[method]
        if isinstance(method_config, str):
            return method_config
        return method_config.get("command", "echo Hello")

    def _get_method_timeout(self, method: str) -> int:
        """Extract the timeout from a method configuration, fallback to global timeout"""
        method_config = self.methods[method]
        if isinstance(method_config, str):
            return self.timeout
        return method_config.get("timeout", self.timeout)

    @classmethod
    def client(cls) -> str:
        return "jumpstarter_driver_shell.client.ShellClient"

    @export
    def get_methods(self) -> list[str]:
        methods = list(self.methods.keys())
        self.logger.debug(f"get_methods called, returning methods: {methods}")
        return methods

    @export
    async def call_method(self, method: str, env, *args) -> AsyncGenerator[tuple[str, str, int | None], None]:
        """
        Execute a shell method with live streaming output.
        Yields (stdout_chunk, stderr_chunk, returncode) tuples.
        returncode is None until the process completes, then it's the final return code.
        """
        self.logger.info(f"calling {method} with args: {args} and kwargs as env: {env}")
        if method not in self.methods:
            raise ValueError(f"Method '{method}' not found in available methods: {list(self.methods.keys())}")
        script = self._get_method_command(method)
        timeout = self._get_method_timeout(method)
        self.logger.debug(f"running script: {script} with timeout: {timeout}")

        try:
            async for stdout_chunk, stderr_chunk, returncode in self._run_inline_shell_script(
                method, script, *args, env_vars=env, timeout=timeout
            ):
                if stdout_chunk:
                    self.logger.debug(f"{method} stdout:\n{stdout_chunk.rstrip()}")
                if stderr_chunk:
                    self.logger.debug(f"{method} stderr:\n{stderr_chunk.rstrip()}")

                if returncode is not None and returncode != 0:
                    self.logger.info(f"{method} return code: {returncode}")

                yield stdout_chunk, stderr_chunk, returncode
        except subprocess.TimeoutExpired as e:
            self.logger.error(f"Timeout expired while running {method}: {e}")
            yield "", f"\nTimeout expired while running {method}: {e}\n", 199

    def _validate_script_params(self, script, args, env_vars):
        """Validate script parameters and return combined environment."""
        combined_env = os.environ.copy()
        if env_vars:
            for key in env_vars:
                if not isinstance(key, str) or not key.isidentifier():
                    raise ValueError(f"Invalid environment variable name: {key}")
                if key in BLOCKED_ENV_VARS or key.startswith(BLOCKED_ENV_PREFIXES):
                    raise ValueError(
                        f"Environment variable '{key}' is blocked for security reasons"
                    )
            combined_env.update(env_vars)

        if not isinstance(script, str) or not script.strip():
            raise ValueError("Shell script must be a non-empty string")

        for arg in args:
            if not isinstance(arg, str):
                raise ValueError(f"All arguments must be strings, got {type(arg)}")

        if self.cwd and not os.path.isdir(self.cwd):
            raise ValueError(f"Working directory does not exist: {self.cwd}")

        return combined_env

    async def _read_stream_with_timeout(self, stream, timeout=0.01, max_bytes=1024):
        """Read data from a stream with a timeout, returning empty bytes if no data is available."""
        if stream is None:
            return b""
        try:
            with anyio.move_on_after(timeout):
                return await stream.receive(max_bytes)
        except EndOfStream:
            pass
        return b""

    async def _read_process_output(self, process, read_all=False):
        """Read data from stdout and stderr streams."""
        stdout_data = ""
        stderr_data = ""

        if process.stdout:
            try:
                if read_all:
                    chunks = []
                    try:
                        while True:
                            chunk = await process.stdout.receive(65536)
                            if chunk:
                                chunks.append(chunk)
                    except EndOfStream:
                        pass
                    raw = b"".join(chunks)
                else:
                    raw = await self._read_stream_with_timeout(process.stdout)
                if raw:
                    stdout_data = raw.decode('utf-8', errors='replace')
            except Exception:
                pass

        if process.stderr:
            try:
                if read_all:
                    chunks = []
                    try:
                        while True:
                            chunk = await process.stderr.receive(65536)
                            if chunk:
                                chunks.append(chunk)
                    except EndOfStream:
                        pass
                    raw = b"".join(chunks)
                else:
                    raw = await self._read_stream_with_timeout(process.stderr)
                if raw:
                    stderr_data = raw.decode('utf-8', errors='replace')
            except Exception:
                pass

        return stdout_data, stderr_data

    async def _run_inline_shell_script(
        self, method, script, *args, env_vars=None, timeout=None
    ) -> AsyncGenerator[tuple[str, str, int | None], None]:
        """Run the given shell script with live streaming output."""
        combined_env = self._validate_script_params(script, args, env_vars)
        cmd = self.shell + [script, method] + list(args)

        self.logger.debug(f"running {method} with cmd: {cmd} and env: {combined_env} and args: {args}")
        process = await anyio.open_process(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=combined_env,
            cwd=self.cwd,
            start_new_session=True,
        )

        start_time = time.monotonic()

        if timeout is None:
            timeout = self.timeout

        while process.returncode is None:
            if time.monotonic() - start_time > timeout:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except (ProcessLookupError, OSError):
                    pass
                terminated = False
                with anyio.move_on_after(5.0):
                    await process.wait()
                    terminated = True
                if not terminated:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                        self.logger.warning(f"SIGTERM failed to terminate {process.pid}, sending SIGKILL")
                    except (ProcessLookupError, OSError):
                        pass
                raise subprocess.TimeoutExpired(cmd, timeout) from None

            try:
                stdout_data, stderr_data = await self._read_process_output(process, read_all=False)

                if stdout_data or stderr_data:
                    yield stdout_data, stderr_data, None

                await anyio.sleep(0.1)

            except Exception:
                break

        returncode = process.returncode
        remaining_stdout, remaining_stderr = await self._read_process_output(process, read_all=True)
        yield remaining_stdout, remaining_stderr, returncode
