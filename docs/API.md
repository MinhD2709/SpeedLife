# API scaffold

`GET /api/health` returns status, configured mode, and `live_integrations_ready: false`.

`POST /api/cheat-sheets` accepts multipart form fields:

- `files`: 1–5 PDF uploads (repeat the same field name).
- `title`: optional string, max 120 characters.

Success shape:

```json
{
  "mode": "demo",
  "title": "Physics",
  "points": [{"text": "Force equals mass times acceleration.", "citation": {
    "source_id": "content-hash", "filename": "lecture.pdf", "page": 1,
    "text": "Force equals mass times acceleration."
  }}],
  "warnings": ["Demo uses source excerpts, not AI summaries; only a small selection is shown."],
  "trace": ["Prepared page-preserving chunks."]
}
```

Pages are one-based. Source IDs derive from PDF content, so identical filenames
cannot silently merge different documents. Invalid, encrypted, over-limit, or
textless PDFs return 422. Missing inputs return 422. Live mode returns 503 until
implemented. Extraction is all-or-nothing across a submitted batch.
