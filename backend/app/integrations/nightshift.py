from __future__ import annotations

import re
from typing import Any

import httpx

from app.config import Settings
from app.integrations.errors import IntegrationNotReady
from app.models import PlanUnit, StudentRecord


UNIT_CODE = re.compile(r"\b[A-Z]{4}\d{4}\b")


class NightshiftClient:
    def __init__(self, settings: Settings | None = None, transport: httpx.AsyncBaseTransport | None = None):
        self.settings = settings or Settings.from_env()
        self.transport = transport

    def _headers(self, *, chat: bool = False) -> dict[str, str]:
        if not self.settings.meterless_runtime_token:
            raise IntegrationNotReady("Meterless Runtime token is missing.")
        headers = {
            "Authorization": f"Bearer {self.settings.meterless_runtime_token}",
            "meterless-app": self.settings.meterless_app_id,
        }
        if chat:
            headers["meterless-scope"] = "user"
            headers["Content-Type"] = "application/json"
        return headers

    async def discover_models(self) -> list[dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=20, transport=self.transport) as client:
                response = await client.get(f"{self.settings.meterless_base_url}/models", headers=self._headers())
            response.raise_for_status()
            payload = response.json()
            models = payload.get("data", []) if isinstance(payload, dict) else []
            return [item for item in models if isinstance(item, dict) and str(item.get("id", "")).startswith("meterless/")]
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in {401, 403}:
                raise IntegrationNotReady("Nightshift rejected the Runtime token.") from exc
            raise IntegrationNotReady(f"Nightshift model discovery failed with HTTP {exc.response.status_code}.") from exc
        except (httpx.RequestError, ValueError) as exc:
            raise IntegrationNotReady(f"Cannot reach or decode Nightshift: {exc}") from exc

    async def health(self) -> None:
        origin = self.settings.meterless_base_url[:-3] if self.settings.meterless_base_url.endswith("/v1") else self.settings.meterless_base_url
        try:
            async with httpx.AsyncClient(timeout=10, transport=self.transport) as client:
                response = await client.get(f"{origin}/healthz")
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise IntegrationNotReady(f"Nightshift health check failed with HTTP {exc.response.status_code}.") from exc
        except httpx.RequestError as exc:
            raise IntegrationNotReady(f"Cannot reach Nightshift health endpoint: {exc}") from exc

    async def _complete(self, prompt: str) -> str:
        body = {
            "model": self.settings.meterless_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You explain an already validated university plan. Do not add, replace, or recommend unit codes. "
                        "State that the outlook is indicative and cite the supplied official links."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        try:
            async with httpx.AsyncClient(timeout=180, transport=self.transport) as client:
                response = await client.post(
                    f"{self.settings.meterless_base_url}/chat/completions", headers=self._headers(chat=True), json=body
                )
            response.raise_for_status()
            payload = response.json()
            content = payload["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("empty message content")
            return content.strip()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in {401, 403}:
                raise IntegrationNotReady("Nightshift rejected the Runtime token.") from exc
            raise IntegrationNotReady(f"Nightshift chat failed with HTTP {exc.response.status_code}.") from exc
        except (httpx.RequestError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise IntegrationNotReady(f"Nightshift returned an unusable response: {exc}") from exc

    async def explain(self, record: StudentRecord, selected: list[PlanUnit], session: str) -> str:
        codes = {item.code for item in selected}
        completed = sorted(unit.code for unit in record.units if unit.status in {"completed", "credited"})
        facts = "\n".join(
            f"- {unit.code} {unit.title}: {unit.reason} Source: {unit.source_url}" for unit in selected
        )
        if self.settings.mode == "demo":
            return (
                f"This {session} plan contains {len(selected)} rule-checked unit(s). "
                "Core requirements are prioritised before selectives. The later outlook is indicative and should be rechecked before enrolment."
            )
        prompt = f"Confirmed completed units: {', '.join(completed) or 'none'}\nValidated {session} plan:\n{facts}"
        for attempt in range(2):
            text = await self._complete(prompt if attempt == 0 else prompt + "\nRewrite using only these unit codes: " + ", ".join(codes))
            unknown = set(UNIT_CODE.findall(text)) - codes - set(completed)
            if not unknown:
                return text
        raise IntegrationNotReady("Nightshift explanation introduced unit codes outside the validated plan.")

    async def status(self) -> dict[str, Any]:
        if self.settings.mode == "demo":
            return {"state": "demo", "model": self.settings.meterless_model, "nemotron_route_confirmed": False}
        await self.health()
        models = await self.discover_models()
        ids = [item["id"] for item in models]
        if self.settings.meterless_model not in ids:
            raise IntegrationNotReady("Configured Meterless route was not returned by model discovery.")
        return {
            "state": "online",
            "model": self.settings.meterless_model,
            "discovered_models": ids,
            "nemotron_route_confirmed": self.settings.meterless_nemotron_route_confirmed,
        }
