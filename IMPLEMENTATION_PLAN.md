# Implementation Plan

This plan deliberately stops after each review gate. No optional AI work begins until the baseline has been reviewed and accepted.

## Stage 0 — Design review (current deliverable)

Deliverables:

- `REQUIREMENTS.md`
- `ACCEPTANCE_CRITERIA.md`
- `ARCHITECTURE.md`
- `IMPLEMENTATION_PLAN.md`

Review decisions needed:

1. Confirm or amend the initial taxonomy and priority definitions.
2. Confirm confidence/review threshold policy and synthetic data scenario coverage.
3. Approve the staged scope and local-only assumptions.

Exit gate: written approval to implement Stage 1.

## Stage 1 — Foundation, deterministic intelligence, and audit trail

1. Create the project skeleton, dependency manifest, formatting/linting choices if desired, and Pytest setup.
2. Define domain enums/models, centralized validation, lifecycle policy, and configuration constants.
3. Implement SQLite bootstrap/migrations, foreign-key enforcement, repositories, and idempotent synthetic seed data.
4. Implement transparent rule-based classification, rule precedence, evidence capture, confidence calculation, and review routing.
5. Implement intake and processing services with transactional persistence of requests and processing runs.
6. Implement review service and a Streamlit review queue that records confirmations/corrections without mutating source decisions.
7. Implement reporting service, KPI definitions, Plotly dashboard views, and explicit empty/error states.
8. Write and run automated unit/integration tests for all Stage 1 acceptance criteria.
9. Write README exact setup, launch, seed, test, and data-safety instructions.

Artifacts for review:

- Local runnable baseline, test results, representative synthetic screenshots/data examples, and documented known limitations.

Exit gate: stakeholder verifies Stage 1 acceptance criteria and authorizes optional local AI work.

## Stage 2 — Optional local Ollama inference — implemented

1. Add an isolated Ollama adapter with explicit local URL/model configuration.
2. Define the model-output schema and robust parser/validator for categories, priorities, confidence, and bounded rationale/evidence.
3. Add mode selection and availability diagnostics in the UI; retain rule-based behavior as baseline/fallback.
4. Persist `ollama_local` attempts with model/version metadata and validation/failure status.
5. Route invalid/low-confidence/unavailable outputs safely to fallback and/or human review per the reviewed policy.
6. Add fixture/mock-based contract tests for success, unavailable service, timeout, malformed JSON, unsupported labels, and low confidence.
7. Update README only with verified local setup and tested behavior; do not make unmeasured quality claims.

Exit gate: optional AI acceptance criteria pass and feature claims are supported by code/tests.

## Stage 3 — Portfolio polish — implemented

1. Improve synthetic scenario breadth and visual presentation.
2. Add export or seed-reset utilities if approved.
3. Add architecture diagrams, annotated screenshots, and a short demo script.
4. Re-run the suite and validate README from a clean environment.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Taxonomy does not match target audience | Keep vocabularies centralized and review them before implementation. |
| Rules look opaque or inconsistent | Persist all matching evidence, test precedence, and show reviewer-visible rationale. |
| SQLite schema evolves during development | Use versioned initialization/migrations and temporary-db integration tests. |
| Local model is unavailable or unreliable | Make it optional, validate strict output, preserve rule baseline, and route uncertainty to review. |
| Dashboard implies unsupported conclusions | Use only persisted synthetic data, state KPI definitions, and show empty states. |
