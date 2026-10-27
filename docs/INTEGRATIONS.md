# Sponsor integrations

## Zetaris

Use `data/zetaris/usyd_2026_cds_create.sql` to register the versioned public JSON
catalogue. The backend sends one SQL statement to the direct REST API with a bearer
key, numeric `X-Org-ID`, fresh UUID `X-Request-ID`, and `source: SqlEditor`.

## Meterless Scout Intent

`backend/app/engines/scout.py` implements the five-stage pipeline, scoped capabilities,
PII/injection guards, five-minute HMAC contracts and verification. The three live
intents plan a term, check unit eligibility and explain degree progress. The JavaScript
adapter in `meterless/scout_adapter.mjs` lets the official eval harness invoke Python.

## Nightshift and Nemotron

Copy the Runtime URL, token and discovered `meterless/*` route from Nightshift's
Console. Put the NVIDIA key only in Nightshift's Providers tab. Seat a Nemotron-backed
lane, then retain a redacted Nightshift run receipt for the demo. The API sends
`meterless-app: unipilot` on every call and `meterless-scope: user` on chat.
