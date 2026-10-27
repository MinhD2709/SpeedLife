# Architecture and scope

Proposed track: The Agent That Can Explain Why (confirm in HackOS).
The supplied guide requires Zetaris, Nightshift, and a working Meterless Engine.
This scaffold alone does not meet those integration requirements.

```text
React upload + result view
    -> POST /api/cheat-sheets
    -> bounded PDF validation + page extraction
    -> ExtractionAgent (page-preserving chunks)
    -> PlanningAgent (demo: round-robin source excerpts)
    -> VerificationAgent (exact excerpts + source/page checks)
        -> if evidence fails: one revision from source excerpts
        -> if still empty: fail, never return unsupported points
    -> cited result + warnings + trace
```

## Live workflow to implement

1. Ingest extracted pages into Zetaris with course, document, page, and chunk IDs.
2. Planner chooses topics and a token budget; retrieve relevant chunks from Zetaris.
3. Nightshift extracts concepts and drafts a compact sheet with structured citations.
4. Verifier fetches original evidence and critiques coverage, definitions, and formulas.
5. Planner revises based on missing evidence, capped at two attempts.
6. Persist run state and revisions through the selected Meterless Engine.
7. Surface the final evidence and step trace; avoid logging raw lectures or secrets.

Sponsor adapters intentionally raise `IntegrationNotReady`; live API mode returns
503 until a real orchestrator and adapters exist. No guessed endpoint paths are used.
The existing demo agent implementation is deterministic and does not call AI.

## Cost and scale

A page is not a fixed number of tokens. Extract locally once; retain page metadata,
cache by content hash, split by token count with the selected model's tokenizer,
and retrieve only relevant chunks. Budget input/output per agent and per run.
The current 1,200-character chunks are a demo bound, not a token measurement.
Do not send all 100-page PDFs to every agent. Add hierarchical lecture summaries,
coverage evaluation, duplicate suppression, and usage accounting for full courses.

PDF parsing currently runs in the API process. Move parsing/OCR and longer agent
runs to an isolated worker with timeouts and job status before supporting untrusted
public traffic or large courses. OCR, tables/formula handling, semantic verification,
authentication, durable storage, job queues, and full-course coverage remain TODO.
