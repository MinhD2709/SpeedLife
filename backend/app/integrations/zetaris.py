from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import httpx

from app.config import Settings
from app.integrations.errors import IntegrationNotReady
from app.models import CatalogUnit


CATALOG_PATH = Path(__file__).parents[1] / "data" / "usyd_2026_cds.json"
CATALOG_SQL = """
SELECT code, title, credit_points, level, requirement_group, core, sessions,
       prerequisites, corequisites, prohibitions, assumed_knowledge, source_url, handbook_year
FROM unipilot.usyd_2026_cds_units
WHERE handbook_year = 2026
""".strip()


def local_catalog() -> list[CatalogUnit]:
    data = json.loads(CATALOG_PATH.read_text())
    return [CatalogUnit.model_validate(item) for item in data["units"]]


class ZetarisRepository:
    def __init__(self, settings: Settings | None = None, transport: httpx.AsyncBaseTransport | None = None):
        self.settings = settings or Settings.from_env()
        self.transport = transport

    def _configured(self) -> bool:
        return bool(self.settings.zetaris_rest_url and self.settings.zetaris_api_key and self.settings.zetaris_org_id)

    async def _run_sql(self, sql: str, limit: int = 1000) -> dict[str, Any]:
        if not self._configured():
            raise IntegrationNotReady("Zetaris REST URL, organization ID, or API key is missing.")
        headers = {
            "Authorization": f"Bearer {self.settings.zetaris_api_key}",
            "X-Org-ID": self.settings.zetaris_org_id,
            "X-Request-ID": str(uuid.uuid4()),
        }
        body = {"queryId": str(uuid.uuid4()), "sql": sql, "source": "SqlEditor", "limit": limit}
        try:
            async with httpx.AsyncClient(timeout=60, transport=self.transport) as client:
                response = await client.post(
                    f"{self.settings.zetaris_rest_url}/sql-editor/sqls/run", headers=headers, json=body
                )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise IntegrationNotReady("Zetaris returned a non-object response.")
            return payload
        except httpx.HTTPStatusError as exc:
            code = exc.response.status_code
            if code in {401, 403}:
                raise IntegrationNotReady("Zetaris rejected the API key or organization ID.") from exc
            if code == 400:
                raise IntegrationNotReady(f"Zetaris rejected the SQL request: {exc.response.text[:240]}") from exc
            raise IntegrationNotReady(f"Zetaris request failed with HTTP {code}.") from exc
        except (httpx.RequestError, ValueError) as exc:
            raise IntegrationNotReady(f"Cannot reach or decode Zetaris: {exc}") from exc

    async def catalog(self) -> list[CatalogUnit]:
        if self.settings.mode == "demo":
            return local_catalog()
        payload = await self._run_sql(CATALOG_SQL)
        rows = payload.get("data")
        if not isinstance(rows, list) or not rows:
            raise IntegrationNotReady("Zetaris returned no USYD catalogue rows.")
        if not isinstance(rows[0], dict):
            columns = payload.get("columns") or payload.get("schema")
            names = [item.get("name") if isinstance(item, dict) else item for item in columns or []]
            if not names:
                raise IntegrationNotReady("Zetaris rows were not named; update the registered view.")
            rows = [dict(zip(names, row, strict=False)) for row in rows]
        return [CatalogUnit.model_validate(row) for row in rows]

    async def status(self) -> dict[str, Any]:
        if self.settings.mode == "demo":
            return {"state": "demo", "query": "local fixture", "units": len(local_catalog())}
        payload = await self._run_sql("SELECT 1 AS one", limit=1)
        return {"state": "online", "query": "SELECT 1", "reply_received": bool(payload.get("data"))}
