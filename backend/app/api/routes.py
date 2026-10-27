from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.agents.orchestrator import UniPilotOrchestrator
from app.config import Settings
from app.integrations.errors import IntegrationNotReady
from app.integrations.nightshift import NightshiftClient
from app.integrations.zetaris import ZetarisRepository
from app.models import PlanRequest, PlanResponse, RecordExtractionResponse
from app.services.student_record import MAX_FILE_BYTES, extract_student_record


router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    settings = Settings.from_env()
    return {"status": "ok", "mode": settings.mode, "product": "UniPilot"}


@router.get("/integrations/status")
async def integration_status():
    settings = Settings.from_env()

    async def checked(name, operation):
        try:
            return await operation()
        except IntegrationNotReady as exc:
            return {"state": "offline", "error": str(exc), "integration": name}

    zetaris = await checked("zetaris", ZetarisRepository(settings).status)
    meterless = await checked("meterless", NightshiftClient(settings).status)
    scout = {
        "state": "offline" if settings.mode == "live" and not settings.scout_signing_ready else "online",
        "registry_version": 1,
        "engine": "Scout Intent",
    }
    if scout["state"] == "offline":
        scout["error"] = "SCOUT_SIGNING_SECRET must be unique and at least 32 characters."
    return {
        "mode": settings.mode,
        "zetaris": zetaris,
        "meterless": meterless,
        "scout": scout,
        "live_ready": (
            zetaris.get("state") == "online"
            and meterless.get("state") == "online"
            and meterless.get("nemotron_route_confirmed") is True
            and scout["state"] == "online"
        ),
    }


@router.post("/student-records/extract", response_model=RecordExtractionResponse)
async def extract_record(files: Annotated[list[UploadFile], File()]):
    loaded: list[tuple[str, bytes]] = []
    try:
        for upload in files:
            content = await upload.read(MAX_FILE_BYTES + 1)
            loaded.append((upload.filename or "academic-record.pdf", content))
        return extract_student_record(loaded)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    finally:
        for upload in files:
            await upload.close()


@router.post("/plans", response_model=PlanResponse)
async def create_plan(request: PlanRequest):
    try:
        return await UniPilotOrchestrator().run(request)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except IntegrationNotReady as exc:
        raise HTTPException(503, str(exc)) from exc
