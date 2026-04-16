from pydantic import BaseModel


class SandboxPolicy(BaseModel):
    enabled: bool = False
