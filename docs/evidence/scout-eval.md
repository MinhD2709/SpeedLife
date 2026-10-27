# Meterless Scout conformance evidence

Run on 28 October 2026 against the official Meterless `scout-intent` v1 smoke corpus (32 examples):

```text
intent_top1          1.0000
intent_top3_recall   1.0000
injection_precision  1.0000
injection_recall     1.0000
tool_precision       1.0000
clarification_rate   0.0625
override_frequency   0.0000 (not measured by the offline corpus)
```

The official documentation describes this corpus as a smoke set, not a published benchmark. Reproduce it from the `engines/scout-intent` directory of the Meterless repository:

```bash
npm install
SCOUT_IMPL="/absolute/path/to/SpeedLife-unipilot/meterless/scout_adapter.mjs" npm run evals
```

The adapter launches the same Python Scout implementation used by the FastAPI application.
