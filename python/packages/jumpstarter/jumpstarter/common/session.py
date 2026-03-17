from dataclasses import dataclass


@dataclass
class SessionMetadata:
    exporter_name: str
    motd: str | None = None
