from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from app.models import DocumentSummary, RecordExtractionResponse, StudentRecord, StudentUnit


UNIT_CODE = re.compile(r"\b([A-Z]{4}\d{4})\b")
MARK = re.compile(r"(?<!\d)(100|[1-9]?\d)(?:\.\d+)?(?!\d)")
MAX_FILE_BYTES = 15 * 1024 * 1024
MAX_TOTAL_BYTES = 30 * 1024 * 1024
MAX_PAGES = 100
STATUS_PRIORITY = {"unknown": 0, "failed": 1, "current": 2, "credited": 3, "completed": 4}


def _status_for(line: str, mark: float | None) -> str:
    lowered = line.lower()
    if any(word in lowered for word in ("enrolled", "current", "in progress")):
        return "current"
    if any(word in lowered for word in ("credit transfer", "recognised prior", "recognized prior", "credited")):
        return "credited"
    if any(word in lowered for word in ("fail", "absent fail", "discontinue fail")) or (mark is not None and mark < 50):
        return "failed"
    if mark is not None or any(word in lowered for word in ("pass", "credit", "distinction", "completed")):
        return "completed"
    return "unknown"


def extract_student_record(files: list[tuple[str, bytes]]) -> RecordExtractionResponse:
    if not 1 <= len(files) <= 2:
        raise ValueError("Upload a transcript and, optionally, one progression report.")
    if sum(len(content) for _, content in files) > MAX_TOTAL_BYTES:
        raise ValueError("Combined PDFs must be below 30 MB.")

    found: dict[str, StudentUnit] = {}
    summaries: list[DocumentSummary] = []
    warnings: list[str] = []
    for raw_name, content in files:
        name = Path(raw_name.replace("\\", "/")).name[:200] or "academic-record.pdf"
        if len(content) > MAX_FILE_BYTES or not content.startswith(b"%PDF-"):
            raise ValueError(f"{name}: use a valid PDF below 15 MB.")
        try:
            reader = PdfReader(BytesIO(content))
        except Exception as exc:
            raise ValueError(f"{name}: could not read this PDF.") from exc
        if reader.is_encrypted:
            raise ValueError(f"{name}: upload an unlocked copy.")
        if len(reader.pages) > MAX_PAGES:
            raise ValueError(f"{name}: PDFs are limited to 100 pages.")

        before = len(found)
        for page_number, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            if not text.strip():
                warnings.append(f"{name}, page {page_number}: no readable text; OCR may be required.")
                continue
            for line in text.splitlines():
                matches = list(UNIT_CODE.finditer(line.upper()))
                for match in matches:
                    code = match.group(1)
                    numbers = [float(item.group(0)) for item in MARK.finditer(line) if int(float(item.group(0))) <= 100]
                    mark = numbers[-1] if numbers else None
                    status = _status_for(line, mark)
                    candidate = StudentUnit(
                        code=code,
                        status=status,
                        mark=mark,
                        source_document=name,
                        page=page_number,
                    )
                    existing = found.get(code)
                    if existing is None or STATUS_PRIORITY[status] > STATUS_PRIORITY[existing.status]:
                        found[code] = candidate
        summaries.append(DocumentSummary(filename=name, pages=len(reader.pages), units_found=len(found) - before))

    if not found:
        warnings.append("No unit codes were detected. Add them manually before confirming the record.")
    if any(unit.status == "unknown" for unit in found.values()):
        warnings.append("Some unit statuses were ambiguous. Check every row before confirming.")
    return RecordExtractionResponse(
        record=StudentRecord(units=sorted(found.values(), key=lambda unit: unit.code)),
        documents=summaries,
        warnings=warnings,
    )
