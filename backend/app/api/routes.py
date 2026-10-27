from dataclasses import asdict
from typing import Annotated
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from app.agents.orchestrator import Orchestrator
from app.config import Settings
from app.services.pdf_extraction import MAX_FILE_BYTES, MAX_TOTAL_BYTES, extract_pdf

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    return {"status": "ok", "mode": Settings.from_env().mode, "live_integrations_ready": False}


@router.post("/cheat-sheets")
async def create_cheat_sheet(
    files: Annotated[list[UploadFile], File()],
    title: Annotated[str, Form(max_length=120)] = "My lecture cheat sheet",
):
    if Settings.from_env().mode != "demo":
        raise HTTPException(503, "Live integrations are not implemented. Use APP_MODE=demo for local development.")
    if not 1 <= len(files) <= 5:
        raise HTTPException(422, "Upload between 1 and 5 lecture PDFs.")
    pages, warnings, total = [], [], 0
    try:
        for upload in files:
            content = await upload.read(MAX_FILE_BYTES + 1)
            total += len(content)
            if total > MAX_TOTAL_BYTES:
                raise ValueError("Combined PDFs must be below 30 MB.")
            extracted, notices = extract_pdf(content, upload.filename or "lecture.pdf")
            pages.extend(extracted)
            warnings.extend(notices)
        return asdict(Orchestrator().run(pages, title.strip() or "My lecture cheat sheet", warnings))
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    finally:
        for upload in files:
            await upload.close()
