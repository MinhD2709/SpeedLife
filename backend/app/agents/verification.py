from app.models import Evidence, Point


class VerificationAgent:
    """Structural/exact-excerpt verification; semantic AI checking is still TODO."""

    def run(self, points: list[Point], pages: list[Evidence]) -> tuple[list[Point], list[str]]:
        sources = {(p.source_id, p.filename, p.page): p.text for p in pages}
        approved, issues = [], []
        for point in points:
            citation = point.citation
            source = sources.get((citation.source_id, citation.filename, citation.page))
            if (not point.text.strip() or source is None or not citation.text.strip()
                    or citation.text not in source or point.text not in citation.text):
                issues.append("Removed a point whose excerpt or page reference could not be verified.")
            else:
                approved.append(point)
        return approved, issues
