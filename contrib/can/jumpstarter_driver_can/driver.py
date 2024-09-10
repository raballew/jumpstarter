from dataclasses import field
from typing import Callable, Optional, Sequence, Tuple, Union
from uuid import UUID, uuid4

import can
import isotp
from pydantic import ConfigDict, validate_call
from pydantic.dataclasses import dataclass

from jumpstarter.driver import Driver, export

from .common import CanMessage, IsoTpAddress, IsoTpAsymmetricAddress, IsoTpMessage, IsoTpParams


@dataclass(kw_only=True, config=ConfigDict(arbitrary_types_allowed=True))
class Can(Driver):
    channel: str | int | None
    interface: str | None
    bus: can.Bus = field(init=False)

    __tasks: dict[UUID, can.broadcastmanager.CyclicSendTaskABC] = field(init=False, default_factory=dict)

    @classmethod
    def client(cls) -> str:
        return "jumpstarter_driver_can.client.CanClient"

    def __post_init__(self):
        super().__post_init__()
        self.bus = can.Bus(channel=self.channel, interface=self.interface)

    @export
    @validate_call(validate_return=True)
    def _recv_internal(self, timeout: Optional[float]) -> Tuple[Optional[CanMessage], bool]:
        msg, filtered = self.bus._recv_internal(timeout)
        if msg:
            return CanMessage.construct(msg), filtered
        return None, filtered

    @export
    @validate_call(validate_return=True)
    def send(self, msg: CanMessage, timeout: float | None = None):
        self.bus.send(can.Message(**msg.__dict__), timeout)

    @export
    @validate_call(validate_return=True, config=ConfigDict(arbitrary_types_allowed=True))
    def _send_periodic_internal(
        self,
        msgs: Union[Sequence[CanMessage], CanMessage],
        period: float,
        duration: Optional[float] = None,
        modifier_callback: Optional[Callable[[can.Message], None]] = None,
    ) -> UUID:
        assert modifier_callback is None
        task = self.bus._send_periodic_internal(msgs, period, duration, modifier_callback)
        uuid = uuid4()
        self.__tasks[uuid] = task
        return uuid

    @export
    @validate_call(validate_return=True)
    def _stop_task(self, uuid: UUID):
        self.__tasks.pop(uuid).stop()

    @export
    @validate_call(validate_return=True)
    def state(self, value: can.BusState | None = None) -> can.BusState | None:
        if value:
            self.bus.state = value
        else:
            return self.bus.state

    @export
    @validate_call(validate_return=True)
    def protocol(self) -> can.CanProtocol:
        return self.bus.protocol

    @export
    @validate_call(validate_return=True)
    def channel_info(self) -> str:
        return self.bus.channel_info

    @export
    # python-can bug
    # https://docs.pydantic.dev/2.8/errors/usage_errors/#typed-dict-version
    # @validate_call(validate_return=True)
    def _apply_filters(self, filters: Optional[can.typechecking.CanFilters]) -> None:
        self.bus._apply_filters(filters)

    @export
    @validate_call(validate_return=True)
    def flush_tx_buffer(self) -> None:
        self.bus.flush_tx_buffer()

    @export
    @validate_call(validate_return=True)
    def shutdown(self) -> None:
        self.bus.shutdown()


@dataclass(kw_only=True, config=ConfigDict(arbitrary_types_allowed=True))
class IsoTp(Driver):
    """
    Pure python ISO-TP socket driver

    Available on any platform, moderate performance and reliability,
    wide support for non-standard hardware interfaces
    """

    channel: str | int | None
    interface: str | None
    address: isotp.Address
    params: IsoTpParams = field(default_factory=IsoTpParams)
    read_timeout: float = 0.05

    bus: can.Bus = field(init=False)
    notifier: can.Notifier = field(init=False)
    stack: isotp.NotifierBasedCanStack = field(init=False)

    @classmethod
    def client(cls) -> str:
        return "jumpstarter_driver_can.client.IsoTpClient"

    def __post_init__(self):
        super().__post_init__()
        self.bus = can.Bus(channel=self.channel, interface=self.interface)
        self.notifier = can.Notifier(self.bus, [])
        self.stack = isotp.NotifierBasedCanStack(
            self.bus,
            self.notifier,
            address=self.address,
            params=self.params.model_dump(),
            read_timeout=self.read_timeout,
        )

    @export
    @validate_call(validate_return=True)
    def start(self) -> None:
        self.stack.start()

    @export
    @validate_call(validate_return=True)
    def stop(self) -> None:
        self.stack.stop()

    @export
    @validate_call(validate_return=True)
    def send(
        self, msg: IsoTpMessage, target_address_type: int | None = None, send_timeout: float | None = None
    ) -> None:
        return self.stack.send(msg.data, target_address_type, send_timeout)

    @export
    @validate_call(validate_return=True)
    def recv(self, block: bool = False, timeout: float | None = None) -> IsoTpMessage:
        return IsoTpMessage.model_construct(data=self.stack.recv(block, timeout))

    @export
    @validate_call(validate_return=True)
    def available(self) -> bool:
        return self.stack.available()

    @export
    @validate_call(validate_return=True)
    def transmitting(self) -> bool:
        return self.stack.transmitting()

    @export
    @validate_call(validate_return=True)
    def set_address(self, address: IsoTpAddress | IsoTpAsymmetricAddress) -> None:
        self.stack.set_address(address.dump())

    @export
    @validate_call(validate_return=True)
    def stop_sending(self) -> None:
        self.stack.stop_sending()

    @export
    @validate_call(validate_return=True)
    def stop_receiving(self) -> None:
        self.stack.stop_receiving()


@dataclass(kw_only=True, config=ConfigDict(arbitrary_types_allowed=True))
class IsoTpSocket(Driver):
    """
    Linux kernel ISO-TP socket driver

    Available since kernel 5.10, good performance and reliability,
    only support standard hardware interfaces
    """

    channel: str
    address: isotp.Address
    params: IsoTpParams = field(default_factory=IsoTpParams)

    sock: isotp.socket | None = field(init=False, default=None)

    @classmethod
    def client(cls) -> str:
        return "jumpstarter_driver_can.client.IsoTpClient"

    @export
    @validate_call(validate_return=True)
    def start(self) -> None:
        if self.sock:
            raise ValueError("socket already started")
        self.sock = isotp.socket()
        self.params.apply(self.sock)
        self.sock.bind(self.channel, self.address)

    @export
    @validate_call(validate_return=True)
    def stop(self) -> None:
        if not self.sock:
            raise ValueError("socket not started")
        self.sock.close()
        self.sock = None

    @export
    @validate_call(validate_return=True)
    def send(
        self, msg: IsoTpMessage, target_address_type: int | None = None, send_timeout: float | None = None
    ) -> None:
        if not self.sock:
            raise ValueError("socket not started")
        self.sock.send(msg.data)

    @export
    @validate_call(validate_return=True)
    def recv(self, block: bool = False, timeout: float | None = None) -> IsoTpMessage:
        if not self.sock:
            raise ValueError("socket not started")
        return IsoTpMessage.model_construct(data=self.sock.recv())

    @export
    @validate_call(validate_return=True)
    def available(self) -> bool:
        raise NotImplementedError

    @export
    @validate_call(validate_return=True)
    def transmitting(self) -> bool:
        raise NotImplementedError

    @export
    @validate_call(validate_return=True)
    def set_address(self, address: IsoTpAddress | IsoTpAsymmetricAddress) -> None:
        raise NotImplementedError

    @export
    @validate_call(validate_return=True)
    def stop_sending(self) -> None:
        raise NotImplementedError

    @export
    @validate_call(validate_return=True)
    def stop_receiving(self) -> None:
        raise NotImplementedError
