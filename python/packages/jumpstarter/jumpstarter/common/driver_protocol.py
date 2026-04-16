from typing import Protocol, runtime_checkable
from uuid import UUID

from jumpstarter_protocol import jumpstarter_pb2


@runtime_checkable
class DriverLike(Protocol):
    uuid: UUID
    labels: dict

    def report(self, *, parent=None, name=None) -> jumpstarter_pb2.DriverInstanceReport: ...

    def enumerate(self, *, root=None, parent=None, name=None) -> list: ...

    def client(self) -> str: ...

    def close(self) -> None: ...

    def reset(self) -> None: ...

    def extra_labels(self) -> dict[str, str]: ...
