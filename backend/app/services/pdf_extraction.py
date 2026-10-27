from hashlib import sha256
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader
from app.models import Evidence

MAX_FILE_BYTES = 15 * 1024 * 1024
MAX_TOTAL_BYTES = 30 * 1024 * 1024
MAX_PAGES = 100
MAX_TEXT_CHARS = 600_000


def extract_pdf(content: bytes, filename: str) -> tuple[list[Evidence], list[str]]:
    if len(content) > MAX_FILE_BYTES or not content.startswith(b"%PDF-"):
        raise ValueError("Use a valid PDF below 15 MB.")
    try:
        reader = PdfReader(BytesIO(content))
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported; upload an unlocked copy.")
        if len(reader.pages) > MAX_PAGES:
            raise ValueError("Each PDF must have at most 100 pages.")
        name = Path(filename.replace("\\", "/")).name[:200] or "lecture.pdf"
        source_id = sha256(content).hexdigest()[:16]
        evidence, warnings, total = [], [], 0
        for page_no, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            total += len(text)
            if total > MAX_TEXT_CHARS:
                raise ValueError("PDF contains too much extracted text; split it into smaller lectures.")
            if not text:
                warnings.append(f"{name}, page {page_no}: no text found; OCR may be needed.")
                continue
            evidence.append(Evidence(source_id, name, page_no, text))
        if not evidence:
            raise ValueError("No readable text found. Scanned PDFs need OCR before upload.")
        return evidence, warnings
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("Could not read this PDF. Try an unlocked, valid text PDF.") from exc
