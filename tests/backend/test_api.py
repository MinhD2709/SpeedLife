from io import BytesIO
import json

import httpx
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from app.config import Settings
from app.integrations.nightshift import NightshiftClient
from app.integrations.zetaris import ZetarisRepository
from app.main import app


client = TestClient(app)


def text_pdf(text="INFO1110 Introduction to Programming 78 Completed"):
    writer = PdfWriter()
    page = writer.add_blank_page(width=500, height=300)
    font = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"), NameObject("/BaseFont"): NameObject("/Helvetica")})
    page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})})
    stream = DecodedStreamObject()
    safe = text.replace("(", "").replace(")", "")
    stream.set_data(f"BT /F1 12 Tf 20 200 Td ({safe}) Tj ET".encode())
    page[NameObject("/Contents")] = writer._add_object(stream)
    output = BytesIO(); writer.write(output); return output.getvalue()


def test_extract_requires_confirmation_and_returns_deidentified_units(monkeypatch):
    monkeypatch.setenv("APP_MODE", "demo")
    response = client.post("/api/student-records/extract", files=[("files", ("transcript.pdf", text_pdf(), "application/pdf"))])
    assert response.status_code == 200
    body = response.json()
    assert body["confirmation_required"] is True
    assert body["record"]["units"][0]["code"] == "INFO1110"
    assert body["record"]["units"][0]["mark"] == 78
    assert "student_id" not in body["record"]


def test_unconfirmed_plan_is_rejected(monkeypatch):
    monkeypatch.setenv("APP_MODE", "demo")
    response = client.post("/api/plans", json={
        "prompt": "plan my next semester", "confirmed": False,
        "record": {"units": [{"code": "INFO1110", "status": "completed"}]},
        "target_session": "Semester 1", "target_credit_points": 24,
        "pace": "balanced", "interests": []
    })
    assert response.status_code == 422


def test_demo_plan_end_to_end(monkeypatch):
    monkeypatch.setenv("APP_MODE", "demo")
    response = client.post("/api/plans", json={
        "prompt": "plan my next semester and explain each choice", "confirmed": True,
        "record": {"units": [{"code": "INFO1110", "status": "completed", "mark": 78}, {"code": "DATA1001", "status": "completed", "mark": 72}]},
        "target_session": "Semester 1", "target_credit_points": 24,
        "pace": "balanced", "interests": ["machine learning"]
    })
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "complete"
    assert body["intent"] == "academic.plan_next_term"
    assert body["contract_id"]
    assert all(unit["source_url"].startswith("https://www.sydney.edu.au/") for unit in body["next_term"])


@pytest.mark.asyncio
async def test_zetaris_headers_and_fresh_uuid():
    seen = []
    async def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"data": [[1]], "columns": ["one"]})
    settings = Settings(mode="live", zetaris_rest_url="http://zetaris/api/v1.0", zetaris_api_key="secret", zetaris_org_id="1")
    repo = ZetarisRepository(settings, httpx.MockTransport(handler))
    await repo.status(); await repo.status()
    assert seen[0].headers["authorization"] == "Bearer secret"
    assert seen[0].headers["x-org-id"] == "1"
    assert seen[0].headers["x-request-id"] != seen[1].headers["x-request-id"]
    assert json.loads(seen[0].content)["source"] == "SqlEditor"


@pytest.mark.asyncio
async def test_nightshift_discovery_and_unknown_code_repair():
    calls = 0
    async def handler(request):
        nonlocal calls
        if request.url.path.endswith("/healthz"):
            return httpx.Response(200, json={"ok": True})
        assert request.headers["authorization"] == "Bearer runtime-secret"
        assert request.headers["meterless-app"] == "unipilot"
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": [{"id": "meterless/auto"}]})
        calls += 1
        text = "Take FAKE9999." if calls == 1 else "Take DATA2001 because it passed the supplied checks."
        return httpx.Response(200, json={"choices": [{"message": {"content": text}}]})
    settings = Settings(mode="live", meterless_runtime_token="runtime-secret", meterless_model="meterless/auto")
    nightshift = NightshiftClient(settings, httpx.MockTransport(handler))
    assert (await nightshift.status())["state"] == "online"
    from app.models import PlanUnit, StudentRecord
    answer = await nightshift.explain(StudentRecord(), [PlanUnit(code="DATA2001", title="Data", credit_points=6, requirement_group="core", reason="eligible", source_url="https://example.com")], "Semester 1")
    assert "DATA2001" in answer
    assert calls == 2
