from dataclasses import dataclass


@dataclass
class SandboxPolicy:
    enabled: bool = False
