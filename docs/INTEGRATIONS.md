# Sponsor integration handoff

The prior chat's assistant responses were unavailable as text. The attached welcome
guide establishes the sponsor requirements but does not supply API contracts.
These are explicit adapter boundaries, not working sponsor integrations.

| Module | Intended feature | Configuration | Remaining work |
| --- | --- | --- | --- |
| `backend/app/integrations/zetaris.py` | Store/retrieve cited lecture pages | `ZETARIS_BASE_URL`, `ZETARIS_API_KEY` | Use the provisioned SQL/REST/SDK interface; add course isolation, parameterized queries, schema and real round-trip tests |
| `backend/app/integrations/nightshift.py` | Primary AI for extraction/planning/verification | `NIGHTSHIFT_BASE_URL`, `NIGHTSHIFT_API_KEY`, `NIGHTSHIFT_MODEL` | Confirm auth, API/SDK, structured outputs, model names, token usage, timeouts and retry behavior from participant resources |
| `backend/app/integrations/meterless_engine.py` | Save and restore workflow checkpoints | `METERLESS_ENGINE_BASE_URL`, `METERLESS_ENGINE_API_KEY`, `METERLESS_ENGINE_NAME` | Select an Engine, confirm its state API, connect checkpoints to the orchestrator, prove recovery after a failed step |

Obtain account-specific values and official API documentation from the HackOS
Participant Setup Guide. Variables are proposed local configuration names, not
claims about vendor conventions. Add only real adapters supported by those docs.
If using an NVIDIA model through Nightshift, configure the provider in Nightshift;
do not add a separate NVIDIA key to this repository.

Before declaring live mode ready: implement the adapters and live orchestration,
add structured response validation and semantic verification, write credential-gated
integration tests, and show evidence of actual Zetaris retrieval, a Nightshift model
call, and Engine checkpoint recovery. Keep those tests opt-in and never print keys.
