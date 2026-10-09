import pandas as pd

from bri.reporting import distributions, kpis


def test_kpis_do_not_fabricate_empty_results():
    frame = pd.DataFrame(columns=["reviewed", "corrected"])
    assert kpis(frame) == {"requests": 0, "review_rate": 0.0, "correction_rate": 0.0}


def test_kpis_and_distributions_use_given_rows():
    frame = pd.DataFrame([
        {"reviewed": 1, "corrected": 1, "proposed_category": "IT Support", "proposed_priority": "High", "processing_mode": "rule_based", "submitted_at_utc": pd.Timestamp("2026-01-01", tz="UTC")},
        {"reviewed": 0, "corrected": 0, "proposed_category": "IT Support", "proposed_priority": "Normal", "processing_mode": "rule_based", "submitted_at_utc": pd.Timestamp("2026-01-01", tz="UTC")},
    ])
    assert kpis(frame) == {"requests": 2, "review_rate": 0.5, "correction_rate": 1.0}
    assert distributions(frame)["category"].iloc[0].to_dict() == {"label": "IT Support", "count": 2}

