# Two-person implementation split

| Owner | Initial responsibility | Handoff |
| --- | --- | --- |
| Builder 1 | Upload, cheat-sheet layout, evidence UI, print/export, error states | Work against `/api/cheat-sheets` response shape |
| Builder 2 | PDF handling, Zetaris schema/retrieval, Nightshift agents, Engine state | Keep API schema stable; publish integration setup and tests |
| Both | Agent feedback loop, coverage checks, end-to-end demo, submission | Review one another's work and run a clean setup |

Suggested next milestones:
1. Run the local demo with two small PDFs.
2. Implement and test Zetaris and Nightshift against official participant resources.
3. Choose and implement a Meterless Engine checkpoint feature.
4. Replace demo planning with AI-backed drafting and bounded evidence-driven revision.
5. Test long PDFs, scans, duplicate filenames, bad inputs, model failures and budgets.
6. Prepare a short demo and document which sponsor calls actually run.

This plan is documentation only; no tasks, messages, commits, or pushes are created.
