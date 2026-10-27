from app.integrations.errors import IntegrationNotReady


class NightshiftClient:
    """Primary live AI boundary. No endpoint or SDK contract is assumed."""

    async def complete_json(self, *, system: str, prompt: str, max_output_tokens: int) -> dict:
        raise IntegrationNotReady("Wire Nightshift using the participant setup guide and a configured model.")
