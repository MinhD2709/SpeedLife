import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mode: str = "demo"
    frontend_origin: str = "http://localhost:5173"

    @classmethod
    def from_env(cls):
        mode = os.getenv("APP_MODE", "demo")
        if mode not in {"demo", "live"}:
            raise ValueError("APP_MODE must be demo or live")
        return cls(mode=mode, frontend_origin=os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"))
