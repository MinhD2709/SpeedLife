from app.agents.extraction import ExtractionAgent
from app.agents.planning import PlanningAgent
from app.agents.verification import VerificationAgent
from app.models import CheatSheet, Evidence


class Orchestrator:
    def __init__(self, planner=None):
        self.extractor = ExtractionAgent()
        self.planner = planner or PlanningAgent()
        self.verifier = VerificationAgent()

    def run(self, pages: list[Evidence], title: str, warnings: list[str]) -> CheatSheet:
        if not pages:
            raise ValueError("No lecture text was supplied.")
        chunks = self.extractor.run(pages)
        points = self.planner.run(chunks)
        approved, issues = self.verifier.run(points, pages)
        trace = [f"Prepared {len(chunks)} page-preserving chunks.",
                 f"Planned {len(points)} excerpts; verified {len(approved)}."]
        if issues:
            # One bounded recovery attempt; never publish unverified points.
            points = PlanningAgent().run(chunks)
            approved, retry_issues = self.verifier.run(points, pages)
            issues += retry_issues
            trace.append("Verification requested revision; replanned once from source excerpts.")
        if not approved:
            raise ValueError("No points passed source verification.")
        return CheatSheet("demo", title, approved,
                          [*warnings, *issues, "Demo uses source excerpts, not AI summaries; only a small selection is shown."], trace)
