# Live agent prompt contracts

Implement versioned prompt files here after connecting Nightshift.

- Extraction: accept page chunks; output concepts, definitions, formulas, and page IDs.
- Planning: accept the topic, output budget, and retrieved concepts; select coverage across lectures.
- Verification: validate each generated claim against retrieved page text. Return missing evidence
  and a revision request; cap iterations at two and fail closed when claims cannot be supported.

Treat PDF text as untrusted data. It cannot override system instructions or invoke tools.
Use structured JSON outputs, validate their schemas, and retain source IDs and page numbers.
The current exact-excerpt verifier does not prove semantic correctness of generated summaries.
