from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from os import getenv, getuid
from typing import ClassVar, Literal

from anyio import (
    connect_tcp,
    connect_unix,
    create_connected_udp_socket,
    create_memory_object_stream,
)
from anyio.streams.stapled import StapledObjectStream

from jumpstarter.driver import Driver, exportstream


class NetworkInterface(metaclass=ABCMeta):
    @classmethod
    def client(cls) -> str:
        return "jumpstarter_driver_network.client.NetworkClient"

    @abstractmethod
    @asynccontextmanager
    async def connect(self): ...


@dataclass(kw_only=True)
class TcpNetwork(NetworkInterface, Driver):
    '''
    TcpNetwork is a driver for connecting to TCP sockets

    >>> addr = getfixture("tcp_echo_server") # start a tcp echo server
    >>> config = f"""
    ... type: jumpstarter_driver_network.driver.TcpNetwork
    ... config:
    ...   host: {addr[0]} # 127.0.0.1
    ...   port: {addr[1]} # random port
    ... """
    >>> with run(config) as tcp:
    ...     with tcp.stream() as conn:
    ...         conn.send(b"hello")
    ...         assert conn.receive() == b"hello"
    '''

    host: str
    port: int

    @exportstream
    @asynccontextmanager
    async def connect(self):
        self.logger.debug("Connecting TCP host=%s port=%d", self.host, self.port)
        async with await connect_tcp(remote_host=self.host, remote_port=self.port) as stream:
            yield stream


@dataclass(kw_only=True)
class UdpNetwork(NetworkInterface, Driver):
    '''
    UdpNetwork is a driver for connecting to UDP sockets

    >>> config = f"""
    ... type: jumpstarter_driver_network.driver.UdpNetwork
    ... config:
    ...   host: 127.0.0.1
    ...   port: 41336
    ... """
    >>> with run(config) as udp:
    ...     pass
    '''

    host: str
    port: int

    @exportstream
    @asynccontextmanager
    async def connect(self):
        self.logger.debug("Connecting UDP host=%s port=%d", self.host, self.port)
        async with await create_connected_udp_socket(remote_host=self.host, remote_port=self.port) as stream:
            yield stream


@dataclass(kw_only=True)
class UnixNetwork(NetworkInterface, Driver):
    '''
    UnixNetwork is a driver for connecting to Unix domain sockets

    >>> config = f"""
    ... type: jumpstarter_driver_network.driver.UnixNetwork
    ... config:
    ...   path: /tmp/example.sock
    ... """
    >>> with run(config) as unix:
    ...     pass
    '''

    path: str

    @exportstream
    @asynccontextmanager
    async def connect(self):
        self.logger.debug("Connecting UDS path=%s", self.path)
        async with await connect_unix(path=self.path) as stream:
            yield stream


@dataclass(kw_only=True)
class DbusNetwork(NetworkInterface, Driver):
    kind: Literal["system", "session"]

    scheme: str | None = field(init=False, default=None)
    args: dict[str, str] = field(init=False, default_factory=dict)

    KIND_LABEL: ClassVar[str] = "jumpstarter.dev/dbusnetwork/kind"

    @classmethod
    def client(cls) -> str:
        return "jumpstarter_driver_network.client.DbusNetworkClient"

    def extra_labels(self):
        return {self.KIND_LABEL: self.kind}

    def __post_init__(self):  # noqa: C901
        if hasattr(super(), "__post_init__"):
            super().__post_init__()

        match self.kind:
            case "system":
                bus = getenv("DBUS_SYSTEM_BUS_ADDRESS", "unix:path=/run/dbus/system_bus_socket")
            case "session":
                bus = getenv("DBUS_SESSION_BUS_ADDRESS", f"unix:path=/run/user/{getuid()}/bus")
            case _:
                raise ValueError(f"invalid bus type: {self.kind}")

        self.scheme, sep, rem = bus.partition(":")
        if not sep:
            raise ValueError(f"invalid bus addr: {bus}")

        for part in rem.split(","):
            key, sep, value = part.partition("=")
            if not sep:
                raise ValueError(f"invalid bus addr: {bus}, missing separator in arguments")
            self.args[key] = value

        match self.scheme:
            case "unix":
                if "path" not in self.args:
                    raise ValueError(f"invalid bus addr: {bus}, missing path argument")
            case "tcp":
                if "host" not in self.args:
                    raise ValueError(f"invalid bus addr: {bus}, missing host argument")
                if "port" not in self.args:
                    raise ValueError(f"invalid bus addr: {bus}, missing port argument")

                try:
                    port = int(self.args["port"])
                except ValueError as e:
                    raise ValueError(f"invalid bus addr: {bus}, invalid port argument") from e
                self.args["port"] = port
            case _:
                raise ValueError(f"invalid bus scheme: {self.scheme}")

    @exportstream
    @asynccontextmanager
    async def connect(self):
        match self.scheme:
            case "unix":
                self.logger.debug("Connecting UDS path=%s", self.args["path"])
                async with await connect_unix(path=self.args["path"]) as stream:
                    yield stream
            case "tcp":
                self.logger.debug("Connecting TCP host=%s port=%d", self.args["host"], self.args["port"])
                async with await connect_tcp(remote_host=self.args["host"], remote_port=self.args["port"]) as stream:
                    yield stream


class EchoNetwork(NetworkInterface, Driver):
    '''
    EchoNetwork is a mock driver implementing the NetworkInterface

    >>> config = """
    ... type: jumpstarter_driver_network.driver.EchoNetwork
    ... """
    >>> with run(config) as echo:
    ...     with echo.stream() as conn:
    ...         conn.send(b"hello")
    ...         assert conn.receive() == b"hello"
    '''

    @exportstream
    @asynccontextmanager
    async def connect(self):
        tx, rx = create_memory_object_stream[bytes](32)
        self.logger.debug("Connecting Echo")
        async with StapledObjectStream(tx, rx) as stream:
            yield stream
