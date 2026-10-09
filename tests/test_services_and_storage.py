from bri.services import RequestService, ReviewService
from bri.seed import seed
from bri.storage import Repository


def payload():
    return {"title": "Unusual request", "description": "Please help with a completely unusual item.", "department": "Operations", "channel": "Portal", "declared_urgency": "Not specified"}


def test_processing_and_review_preserve_audit_history(tmp_path):
    repo = Repository(tmp_path / "test.db")
    repo.initialize()
    request_id, decision = RequestService(repo).submit_and_process(payload(), request_id="r-1")
    queued = repo.requests_for_review()
    assert request_id == "r-1"
    assert len(queued) == 1
    assert queued[0]["processing_mode"] == "rule_based"
    assert queued[0]["processed_at_utc"].endswith("+00:00")
    ReviewService(repo).review("r-1", queued[0]["processing_run_id"], "Alex", "General Inquiry", "Normal", "Confirmed after analysis", decision.category, decision.priority)
    assert repo.requests_for_review() == []
    rows = repo.report_rows()
    assert rows[0]["status"] == "reviewed"
    assert rows[0]["reviewed"] == 1
    assert rows[0]["corrected"] == 1


def test_foreign_keys_are_enforced(tmp_path):
    repo = Repository(tmp_path / "test.db")
    repo.initialize()
    import pytest
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        repo.insert_review({"review_id": "v", "request_id": "missing", "processing_run_id": "missing", "reviewer_name": "Alex", "reviewed_at_utc": "2026-01-01T00:00:00+00:00", "final_category": "General Inquiry", "final_priority": "Normal", "category_corrected": 0, "priority_corrected": 0, "rationale": ""})


def test_synthetic_seed_is_idempotent(tmp_path):
    repo = Repository(tmp_path / "seed.db")
    repo.initialize()
    assert seed(repo) == 6
    assert seed(repo) == 0
    rows = repo.report_rows()
    assert len(rows) == 6
    assert any(row["status"] == "reviewed" and row["corrected"] == 1 for row in rows)
