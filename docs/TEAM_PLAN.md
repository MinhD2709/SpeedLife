# Two-person implementation split

| Owner | Initial responsibility | Handoff |
| --- | --- | --- |
| Builder 1 | Transcript review, planner controls, cited plan UI and error states | Work against `/api/student-records/extract` and `/api/plans` |
| Builder 2 | Zetaris catalogue, deterministic solver, Scout and Nightshift | Keep the API schema stable; publish integration checks and receipts |
| Both | Redacted fixture checks, live sponsor smoke test and demo | Review one another's work and run a clean setup |

Suggested next milestones:
1. Validate parsing against the redacted transcript and progression report.
2. Load the fixed 2026 catalogue into Zetaris and pass the live query check.
3. Run the official Scout eval harness against the adapter.
4. Connect Nightshift, discover the selected route and capture a Nemotron receipt.
5. Run the end-to-end upload, confirmation and plan demo.

This plan is documentation only; no tasks, messages, commits, or pushes are created.
