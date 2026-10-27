from app.integrations.errors import IntegrationNotReady


class MeterlessEngineClient:
    """Planned Engine feature: shared workflow state and bounded retry checkpoints."""

    async def checkpoint(self, run_id: str, state: dict) -> None:
        raise IntegrationNotReady("Select and implement a Meterless Engine using its documented API.")

    async def restore(self, run_id: str) -> dict:
        raise IntegrationNotReady("Implement Engine checkpoint restoration.")
