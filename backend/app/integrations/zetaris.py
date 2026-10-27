from app.integrations.errors import IntegrationNotReady
from app.models import Evidence


class ZetarisRepository:
    """Persist/retrieve page evidence through Zetaris in live mode."""

    async def store_pages(self, course_id: str, pages: list[Evidence]) -> None:
        raise IntegrationNotReady("Implement Zetaris storage against your provisioned data layer.")

    async def search_pages(self, course_id: str, query: str, limit: int = 12) -> list[Evidence]:
        raise IntegrationNotReady("Implement scoped, parameterized Zetaris retrieval.")
