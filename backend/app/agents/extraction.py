from app.models import Evidence


class ExtractionAgent:
    """Prepare bounded, page-preserving chunks for the planning agent."""

    def run(self, pages: list[Evidence], chunk_chars: int = 1200) -> list[Evidence]:
        if chunk_chars < 1:
            raise ValueError("chunk_chars must be positive")
        return [Evidence(page.source_id, page.filename, page.page, page.text[start:start + chunk_chars])
                for page in pages for start in range(0, len(page.text), chunk_chars)]
