# Business Request Intelligence and Automation System

## 1. Purpose

Build a local, portfolio-quality application that receives synthetic business requests, validates and classifies them, routes ambiguous items for human review, stores a complete audit trail, and presents operational and quality reporting. The product must be useful without any AI model. A local Ollama-powered inference option may be added later only when it is implemented, validated, and tested.

## 2. Scope

### In scope

- A Python application with a Streamlit interface.
- Synthetic seed data only; no customer, employee, or production data.
- A deterministic, rule-based classification baseline.
- Request intake, validation, classification, confidence handling, human review, reviewer corrections, persistence, and reporting.
- SQLite persistence, Pandas transformations, Plotly visualizations, and Pytest automated tests.
- Auditable capture of processing mode, timestamps, classification decisions, review actions, and corrections.
- Optional, local-only Ollama inference after the baseline is complete.

### Out of scope for the initial release

- Paid APIs, hosted LLMs, cloud storage, authentication providers, email/Slack integrations, and deployment automation.
- Real-world business data or claims about measured business impact.
- Fully automated closure or assignment of an uncertain request without review.
- AI performance claims unless backed by implemented tests and documented evaluation data.

## 3. User roles and primary workflows

| Role | Goal | Primary workflow |
| --- | --- | --- |
| Request submitter | Enter a business request and understand its disposition | Complete the intake form, submit, receive a tracking ID and current status. |
| Business analyst / reviewer | Resolve uncertain or incorrect classifications | Open review queue, inspect request and rule evidence, choose/correct category and priority, record optional rationale, submit decision. |
| Operations manager | Monitor work volume, routing quality, and review workload | Filter dashboard period, view counts and trends, inspect review/correction metrics, export tabular results if implemented. |
| System maintainer | Configure deterministic logic safely | Change versioned business-rule configuration/code, run tests, and retain rule version on each processing record. |

## 4. Functional requirements

### 4.1 Request intake and validation

1. The system shall accept a request title, description, requester department, request channel, and optional declared urgency.
2. The system shall reject missing required fields, whitespace-only values, unsupported enumerations, and values exceeding configured length limits.
3. The system shall normalize safe input representations (for example, trimming surrounding whitespace) while retaining the original submitted text for auditability if normalization is introduced.
4. The system shall generate a unique request identifier and submission timestamp only after validation succeeds.
5. Seed records shall be visibly identified as synthetic.

### 4.2 Rule-based baseline classification

1. The initial classification engine shall be deterministic and independent of network services or Ollama.
2. It shall produce a category, priority, confidence score, rule-evidence list, rule version, and processing mode of `rule_based`.
3. Categories and priorities shall be configured from a controlled vocabulary. Initial vocabulary, subject to review:
   - Categories: Access & Permissions, Data & Reporting, Finance & Procurement, HR & People Operations, IT Support, Compliance & Risk, General Inquiry.
   - Priorities: Critical, High, Normal, Low.
4. Rules shall use transparent signals such as normalized keywords, requester-provided urgency, and high-risk phrases; classification code shall not be embedded in Streamlit UI callbacks.
5. Conflicting rules shall have documented precedence and preserve every matching rule as evidence.
6. A classification below its configured confidence threshold, with conflicting high-priority signals, or with no category rule match shall be marked `needs_review`.
7. High-risk terms may raise priority but must not silently bypass review when evidence is contradictory or weak.

### 4.3 Human review and correction

1. A reviewer shall be able to list and filter requests with `needs_review` status.
2. The reviewer shall see source text, proposed labels, confidence, processing mode, timestamp, and rule/AI evidence available for that decision.
3. The reviewer shall choose final category and priority from controlled vocabularies, submit a decision, and optionally supply a correction rationale.
4. The system shall record reviewer identifier (local display name or configured placeholder), review timestamp, original proposed values, final values, and whether each field was corrected.
5. A reviewed request shall transition to `reviewed`; a human correction shall never overwrite the original automated result.
6. The UI shall permit a reviewer to confirm an automated result, not only replace it.

### 4.4 Storage and auditability

1. SQLite shall store requests, processing decisions, review decisions, and application metadata in normalized tables with foreign keys enabled.
2. Each processing attempt shall be append-only and shall include mode, timestamp, engine/rule version, raw output (where safe), validated output, confidence, and error/validation status.
3. Processing modes shall include at least `rule_based`; `ollama_local` shall exist only when that optional feature is implemented.
4. All timestamps shall be stored in UTC using an unambiguous ISO-8601 representation and displayed clearly in the interface.
5. Database initialization and synthetic seeding shall be idempotent.

### 4.5 Reporting

1. Reports shall use stored data only and must show an explicit empty state instead of fabricated values when no data matches the selected filters.
2. Initial dashboard metrics shall include request volume, category distribution, priority distribution, review rate, correction rate, and processing-mode counts.
3. Trend and distribution views shall be produced with Plotly from Pandas-prepared data.
4. Reporting logic shall be separate from Streamlit rendering and return testable data structures.
5. Any KPI definition shown in the UI shall be documented, including numerator, denominator, period, and exclusions.

### 4.6 Optional local Ollama stage (not part of baseline)

1. The optional AI mode shall be disabled or unavailable by default when Ollama or a configured local model cannot be reached.
2. It shall submit only the data required for the task to a local Ollama endpoint and clearly label the decision mode `ollama_local`.
3. It shall require machine-readable structured output validated against an application-owned schema and controlled vocabularies.
4. Invalid, incomplete, unsupported, or low-confidence model output shall fall back to `needs_review`; it shall not be stored as a final classification.
5. Rule-based output remains available as a fallback and comparison baseline.
6. README and UI may describe the feature as available only after its implementation, integration tests, and a reproducible local setup are complete.

## 5. Non-functional requirements

- **Local-first:** Application works offline after local dependencies are installed, except optional Ollama connectivity on localhost.
- **Maintainability:** Business rules, classification orchestration, database access, report calculations, and UI reside in separate modules.
- **Reliability:** Expected invalid input and recoverable dependency failures produce actionable messages, not uncaught tracebacks in the UI.
- **Security and privacy:** Use synthetic data only. Validate all external/model outputs before storage. Parameterize SQL. Do not execute model-provided instructions or queries.
- **Accessibility/usability:** Forms have labels, validation messages identify the field/problem, and review actions show confirmation.
- **Reproducibility:** Fixed synthetic seed generator or committed seed dataset, pinned/compatible dependencies, and exact setup instructions.
- **Quality:** Unit tests cover rules, validators, storage, reports, and review transitions. Optional AI tests use mocks/fixtures, never require a paid or remote service.

## 6. Data and state model

Core entities:

- `requests`: submitted synthetic request and immutable intake attributes.
- `processing_runs`: append-only automated attempts, including `processing_mode`, output validation outcome, confidence, evidence, and engine version.
- `reviews`: human decisions linked to a request and its proposed processing run.
- `app_metadata` (optional): schema version and seed version.

Suggested request lifecycle:

`submitted` → `classified` or `needs_review` → `reviewed`

`classified` indicates a validated, sufficiently confident automated result. `needs_review` indicates no autonomous final result. `reviewed` indicates a human confirmed or corrected the proposed result.

## 7. Assumptions to confirm during review

1. The initial taxonomy above is suitable for the portfolio demonstration.
2. A local reviewer display name is sufficient for v1; no authentication is required.
3. Request urgency is an input signal, not automatic proof of priority.
4. Initial review is single-decision per request; a later audit/re-review feature can append another review record if needed.
5. The project will be delivered as a local repository application with a sample SQLite database created at runtime.
