import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mode: str = "demo"
    frontend_origin: str = "http://localhost:5173"
    zetaris_rest_url: str = ""
    zetaris_org_id: str = "1"
    zetaris_api_key: str = ""
    meterless_base_url: str = "http://127.0.0.1:8088/v1"
    meterless_runtime_token: str = ""
    meterless_model: str = "meterless/auto"
    meterless_app_id: str = "unipilot"
    meterless_nemotron_route_confirmed: bool = False
    scout_signing_secret: str = "demo-only-change-me"

    @property
    def scout_signing_ready(self) -> bool:
        return len(self.scout_signing_secret) >= 32 and self.scout_signing_secret != "demo-only-change-me"

    @classmethod
    def from_env(cls) -> "Settings":
        mode = os.getenv("APP_MODE", "demo").lower()
        if mode not in {"demo", "live"}:
            raise ValueError("APP_MODE must be demo or live")
        base_url = os.getenv("METERLESS_BASE_URL", "http://127.0.0.1:8088/v1").rstrip("/")
        for suffix in ("/chat/completions", "/models"):
            if base_url.endswith(suffix):
                base_url = base_url[: -len(suffix)]
        if not base_url.endswith("/v1"):
            base_url += "/v1"
        return cls(
            mode=mode,
            frontend_origin=os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
            zetaris_rest_url=os.getenv("ZETARIS_REST_URL", "").rstrip("/"),
            zetaris_org_id=os.getenv("ZETARIS_ORG_ID", "1"),
            zetaris_api_key=os.getenv("ZETARIS_API_KEY", ""),
            meterless_base_url=base_url,
            meterless_runtime_token=os.getenv("METERLESS_RUNTIME_TOKEN", ""),
            meterless_model=os.getenv("METERLESS_MODEL", "meterless/auto"),
            meterless_app_id=os.getenv("METERLESS_APP_ID", "unipilot"),
            meterless_nemotron_route_confirmed=os.getenv("METERLESS_NEMOTRON_ROUTE_CONFIRMED", "false").lower()
            in {"1", "true", "yes"},
            scout_signing_secret=os.getenv("SCOUT_SIGNING_SECRET", "demo-only-change-me"),
        )
