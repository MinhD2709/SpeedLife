from io import BytesIO
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
from app.main import app
from app.models import Evidence
from app.services.pdf_extraction import extract_pdf

client = TestClient(app)


def text_pdf():
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)
    font = DictionaryObject({NameObject("/Type"): NameObject("/Font"),
                             NameObject("/Subtype"): NameObject("/Type1"),
                             NameObject("/BaseFont"): NameObject("/Helvetica")})
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})})
    stream = DecodedStreamObject()
    stream.set_data(b"BT /F1 12 Tf 20 200 Td (Force equals mass times acceleration.) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(stream)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def test_pdf_upload_end_to_end(monkeypatch):
    monkeypatch.setenv("APP_MODE", "demo")
    response = client.post("/api/cheat-sheets", files=[("files", ("lecture.pdf", text_pdf(), "application/pdf"))])
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "demo"
    assert body["points"][0]["text"] == "Force equals mass times acceleration."
    assert body["points"][0]["citation"]["page"] == 1


def test_invalid_pdf_is_rejected(monkeypatch):
    monkeypatch.setenv("APP_MODE", "demo")
    response = client.post("/api/cheat-sheets", files=[("files", ("fake.pdf", b"not a PDF"))])
    assert response.status_code == 422


def test_scan_without_text_is_rejected():
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    output = BytesIO()
    writer.write(output)
    with pytest.raises(ValueError, match="OCR"):
        extract_pdf(output.getvalue(), "scan.pdf")


def test_page_limit_is_enforced():
    writer = PdfWriter()
    for _ in range(101):
        writer.add_blank_page(width=20, height=20)
    output = BytesIO()
    writer.write(output)
    with pytest.raises(ValueError, match="100 pages"):
        extract_pdf(output.getvalue(), "long.pdf")


def test_live_mode_never_silently_uses_demo(monkeypatch):
    monkeypatch.setenv("APP_MODE", "live")
    response = client.post("/api/cheat-sheets", files=[("files", ("lecture.pdf", text_pdf()))])
    assert response.status_code == 503


def test_total_upload_limit(monkeypatch):
    monkeypatch.setenv("APP_MODE", "demo")
    with patch("app.api.routes.MAX_TOTAL_BYTES", 3):
        response = client.post("/api/cheat-sheets", files=[("files", ("lecture.pdf", b"%PDF-test"))])
    assert response.status_code == 422
