# API

- `GET /api/health` — process and mode health.
- `GET /api/integrations/status` — Zetaris SQL, Nightshift discovery, Scout registry and live readiness.
- `POST /api/student-records/extract` — one or two PDF fields named `files`; returns a de-identified editable record draft.
- `POST /api/plans` — confirmed record, prompt, target session, load, pace and interests; returns a clarification or verified plan.

`POST /api/plans` returns 422 for an unconfirmed/invalid record, 403 when Scout
blocks the request, and 503 when a required live sponsor service is unavailable.
