import json
from urllib.error import URLError

from bri.domain import IntakeCommand
from bri.ollama import OllamaAdapter
from bri.services import RequestService
from bri.storage import Repository


def command():
    return IntakeCommand("Access request", "Please grant VPN access for a new user.", "IT", "Portal", "Normal")


def transport_with(response: dict):
    def transport(url, payload, timeout):
        assert url.endswith("/api/generate")
        assert payload["stream"] is False
        return json.dumps(response).encode()
    return transport


def test_valid_ollama_contract_response_is_accepted():
    adapter = OllamaAdapter(model="test-model", transport=transport_with({"response": json.dumps({"category": "Access & Permissions", "priority": "Normal", "confidence": 0.93, "rationale": "Access terms are present."})}))
    result = adapter.classify(command())
    assert result.error is None
    assert result.decision.category == "Access & Permissions"
    assert not result.decision.requires_review


def test_malformed_or_unsupported_model_output_is_rejected_and_retained():
    adapter = OllamaAdapter(transport=transport_with({"response": '{"category":"not allowed"}'}))
    result = adapter.classify(command())
    assert result.decision is None
    assert result.raw_output == '{"category":"not allowed"}'
    assert "failed validation" in result.error


def test_low_confidence_output_requires_review():
    adapter = OllamaAdapter(transport=transport_with({"response": json.dumps({"category": "Access & Permissions", "priority": "Normal", "confidence": 0.2, "rationale": "Weak signal."})}))
    result = adapter.classify(command())
    assert result.decision.requires_review


def test_unavailable_ollama_falls_back_to_rule_based_and_audits_failure(tmp_path):
    def unavailable(url, payload, timeout):
        raise URLError("offline")
    repo = Repository(tmp_path / "test.db")
    repo.initialize()
    request_id, decision = RequestService(repo).submit_and_process(
        {"title": "VPN access request", "description": "Please grant VPN access and account permission.", "department": "IT", "channel": "Portal", "declared_urgency": "Normal"},
        processing_mode="ollama_local", ollama=OllamaAdapter(transport=unavailable),
    )
    assert decision.category == "Access & Permissions"
    with repo.connection() as conn:
        runs = conn.execute("SELECT processing_mode, validation_status FROM processing_runs WHERE request_id=? ORDER BY processed_at_utc", (request_id,)).fetchall()
    assert [tuple(row) for row in runs] == [("rule_based", "valid"), ("ollama_local", "invalid")]
