from app.models import Evidence, Point


class PlanningAgent:
    """Demo selection. Replace with budgeted Nightshift planning in live mode."""

    def run(self, chunks: list[Evidence], limit: int = 8) -> list[Point]:
        # Round-robin across documents avoids taking every point from the first lecture.
        groups: dict[str, list[Evidence]] = {}
        for chunk in chunks:
            groups.setdefault(chunk.source_id, []).append(chunk)
        selected: list[Point] = []
        while any(groups.values()) and len(selected) < limit:
            for group in groups.values():
                if group and len(selected) < limit:
                    chunk = group.pop(0)
                    selected.append(Point(chunk.text, chunk))
        return selected
