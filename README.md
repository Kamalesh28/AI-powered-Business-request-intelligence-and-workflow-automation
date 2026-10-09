# Business Request Intelligence and Automation System

A local Streamlit demonstration of transparent business-request intake, rule-based classification, human review, audit trails, and operational reporting. It uses **synthetic data only** and requires no paid API, cloud service, or model.

## Implemented scope

- Validated intake form with controlled department, channel, and urgency values.
- Deterministic rule-based category/priority classification with visible matching-rule evidence.
- Confidence-based and conflict/no-match routing to a human review queue.
- SQLite audit records for requests, automated processing runs, reviewer confirmations/corrections, modes, and UTC timestamps.
- Pandas/Plotly dashboard based only on stored data; empty filters produce empty states, not invented KPIs.
- Idempotent synthetic demo seed data.
- Pytest coverage for validation, rules, storage audit fields, review transitions, and reports.

## Optional local Ollama mode

The application works fully without Ollama. If you select **Optional local Ollama**, it connects only to `http://127.0.0.1:11434` by default and uses model `llama3.2`. You may set `BRI_OLLAMA_URL` and `BRI_OLLAMA_MODEL` before launch to use another local endpoint/model.

The service response must be exact JSON with allowed categories, priorities, a 0–1 confidence, and a bounded rationale. Malformed, unsupported, unavailable, or low-confidence output is never used as an autonomous final result: it is recorded for audit and either falls back to the rule decision or routes to human review. Ollama behavior is contract-tested with mocks; no live local model is required by the test suite. This project makes no model quality or accuracy claim.

## Setup

Requires Python 3.11 or later.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run

```powershell
streamlit run app.py
```

The database is created at `data/business_requests.db`. Use **Seed synthetic demo data** from the sidebar to load the repeatable sample dataset. Re-running it will not add duplicates.

For a repeatable command-line demo seed and summary:

```powershell
python scripts/demo.py
```

## Test

```powershell
pytest
```

## KPI definitions

- **Requests:** count of requests in the active filter period.
- **Review rate:** requests that had one or more review records ÷ requests in the active filter.
- **Correction rate:** reviewed requests with a changed category or priority ÷ reviewed requests in the active filter. Confirmed decisions are included in the denominator and are not corrections.
- **Mode counts:** processing-run counts by processing mode. Stage 1 contains only `rule_based`.

All stored timestamps use ISO-8601 UTC. The app is intended for local portfolio demonstration, not production operations.

## Portfolio walkthrough

See [PORTFOLIO_GUIDE.md](PORTFOLIO_GUIDE.md) for a concise demo script, architecture talking points, and evidence to capture. The reporting page now supports department, processing-mode, and request-status filters plus CSV export of only the filtered synthetic data.
