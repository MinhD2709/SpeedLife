from __future__ import annotations

from app.config import Settings
from app.engines.scout import Scout
from app.integrations.errors import IntegrationNotReady
from app.integrations.nightshift import NightshiftClient
from app.integrations.zetaris import ZetarisRepository
from app.models import Clarification, EvidenceLink, PlanRequest, PlanResponse
from app.services.semester_planner import make_plan


class UniPilotOrchestrator:
    def __init__(self, settings: Settings | None = None, zetaris=None, nightshift=None, scout=None):
        self.settings = settings or Settings.from_env()
        self.zetaris = zetaris or ZetarisRepository(self.settings)
        self.nightshift = nightshift or NightshiftClient(self.settings)
        self.scout = scout or Scout(signing_secret=self.settings.scout_signing_secret)

    async def run(self, request: PlanRequest) -> PlanResponse:
        if self.settings.mode == "live" and not self.settings.scout_signing_ready:
            raise IntegrationNotReady(
                "SCOUT_SIGNING_SECRET must be a unique value of at least 32 characters before live mode can issue contracts."
            )
        if not request.confirmed:
            raise ValueError("Review and confirm the extracted academic record before planning.")
        decision = self.scout.decide(
            prompt=request.prompt,
            surface="planner",
            context={"confirmed": True, "target_session": request.target_session},
        )
        if decision.risk["level"] == "block":
            raise PermissionError(decision.risk.get("reason", "Scout blocked this request."))
        if decision.clarification:
            return PlanResponse(
                status="clarification",
                clarification=Clarification.model_validate(decision.clarification),
                intent=decision.intent["primary"],
            )
        if not self.scout.verify(decision.executionContract or {}):
            raise PermissionError("Scout execution contract failed verification.")

        catalog = await self.zetaris.catalog()
        result = make_plan(
            catalog,
            request.record,
            request.target_session,
            request.target_credit_points,
            request.interests,
            request.pace,
        )
        narrative = await self.nightshift.explain(request.record, result.selected, request.target_session)
        evidence = []
        for unit in result.selected:
            if unit.source_url not in {item.url for item in evidence}:
                evidence.append(EvidenceLink(label=f"USYD handbook: {unit.requirement_group}", url=unit.source_url))
        contract = decision.executionContract or {}
        return PlanResponse(
            status="complete",
            next_term=result.selected,
            excluded=result.excluded,
            outlook=result.outlook,
            narrative=narrative,
            evidence=evidence,
            trace=[
                f"Scout routed {decision.intent['primary']} at confidence {decision.intent['confidence']:.2f}.",
                f"Loaded {len(catalog)} handbook unit records through {'the local demo fixture' if self.settings.mode == 'demo' else 'Zetaris'}.",
                f"Deterministically validated {len(result.selected)} units against prerequisites, corequisites, prohibitions, session and load.",
                f"Requested the explanation through Meterless route {self.settings.meterless_model}.",
            ],
            contract_id=contract.get("contractId"),
            intent=decision.intent["primary"],
        )
