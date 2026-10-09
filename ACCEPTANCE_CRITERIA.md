# Acceptance Criteria

## Stage 1 — Foundation and rule-based baseline

| ID | Given | When | Then |
| --- | --- | --- | --- |
| AC-01 | A clean local checkout with documented prerequisites | The documented setup commands are followed | The Streamlit application starts and initializes a local SQLite database without a cloud account or paid API. |
| AC-02 | The initialized application | A user opens the application | Synthetic sample data is available or can be created idempotently and is visibly identified as synthetic. |
| AC-03 | An intake form | A user submits missing, whitespace-only, oversized, or invalid-enum values | The request is not persisted; field-level, actionable validation feedback is shown. |
| AC-04 | A valid request | The user submits it | A unique ID and UTC submission time are stored, and the UI shows the resulting status. |
| AC-05 | A valid request matching configured deterministic signals | It is processed in baseline mode | The persisted processing run has `rule_based` mode, valid controlled-vocabulary labels, confidence, rule version, timestamp, and human-readable evidence. |
| AC-06 | A request matching conflicting rules, no category rule, or below-threshold confidence | It is processed | It receives `needs_review` and appears in the review queue; it is not represented as an autonomous final result. |
| AC-07 | A request in the review queue | A reviewer confirms or changes labels | A review record stores reviewer, timestamp, proposed values, final values, and correction flags; the original automated processing run remains unchanged. |
| AC-08 | Stored requests/processing/reviews | Reports are rendered with filters | Counts and charts derive from the filtered stored data, show definitions for KPI calculations, and display an empty state rather than invented metrics. |
| AC-09 | The test suite | It is executed locally | Tests pass for validators, rule precedence/confidence, persistence/audit fields, review transitions, and report calculations. |
| AC-10 | A database error or malformed internal/model-style output | The application handles it | The UI receives a safe actionable message, the failure is recorded where applicable, and no malformed output becomes a final classification. |

## Stage 2 — Optional local Ollama inference

| ID | Given | When | Then |
| --- | --- | --- | --- |
| AC-11 | Ollama is absent, unreachable, or the configured model is unavailable | A user selects local AI mode | The interface clearly identifies the mode as unavailable or safely falls back to rule-based processing; normal intake and review remain functional. |
| AC-12 | A reachable, configured local Ollama model | It returns schema-valid allowed labels and confidence | The system records an `ollama_local` processing run with validated output, model identifier, timestamp, and raw response retained only as safe audit data. |
| AC-13 | Local AI returns malformed JSON, unsupported labels, missing fields, or low confidence | Output validation runs | The output is rejected, the request is routed to `needs_review` (and/or a documented rule-based fallback is recorded), and the invalid output is never used as a final result. |
| AC-14 | The optional AI code is present | Automated tests run without Ollama | Contract and failure-path tests pass using fixtures/mocks; no test needs network access, a paid API, or a real model. |

## Definition of Done for a stage

- All acceptance criteria for the stage have demonstrable evidence.
- README setup/run/test instructions have been verified from a clean environment where practical.
- No real business data, credentials, cloud dependency, or untested AI claim has been introduced.
- The completed stage is reviewed before work begins on the next one.
