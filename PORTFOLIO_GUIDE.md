# Portfolio Walkthrough

## What this project demonstrates

This application treats automation as a controlled business process rather than a black box. It combines deterministic policy, optional local AI, human decision-making, and traceable reporting in one local-first system.

## Suggested five-minute demo

1. Run `python scripts/demo.py`, then `streamlit run app.py`.
2. Open **Reporting** to show that every dashboard value is generated from stored synthetic data and can be filtered/exported.
3. Open **Submit request**, enter `VPN and payroll access needed`, and choose rule-based mode. Explain why conflicting signals route the request to review.
4. Open **Human review**, show the original request, confidence, processing mode, timestamps, and matching-rule evidence. Confirm or correct the proposal and explain that the system retains the original automation result.
5. Return to **Reporting** and point out review/correction KPIs and the CSV export.
6. Select **Optional local Ollama** for a second request. Explain that it sends only to a configurable localhost endpoint, validates strict structured output, keeps the rule baseline, and falls back safely if unavailable.

## Architecture talking points

- Streamlit is intentionally thin: it renders forms and charts, while services coordinate domain validation, classification, and storage.
- Business rules live separately from both UI and SQLite code, are versioned as `rules-v1`, and expose each matching signal.
- Processing runs are append-only. Review records reference the exact automated run they confirm or correct.
- The optional model adapter is isolated from the domain, does not accept arbitrary labels, and has contract tests without requiring a live model.

## Evidence to include in a portfolio post

- A dashboard screenshot populated exclusively by the built-in synthetic seed data.
- A review-queue screenshot showing rule/AI evidence and a correction action.
- Test output showing `python -m pytest` passing.
- A short excerpt from [ARCHITECTURE.md](ARCHITECTURE.md) alongside the rule and output-validation modules.

Do not claim predictive accuracy, throughput gains, or business impact: this is a synthetic-data portfolio demonstration and no empirical model evaluation is included.
