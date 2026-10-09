from bri.domain import IntakeCommand, Priority
from bri.rules import classify


def command(text: str, urgency: str = "Normal"):
    return IntakeCommand("Request", text, "IT", "Portal", urgency)


def test_clear_rule_is_classified_with_evidence():
    decision = classify(command("Need VPN access and permission for a new account."))
    assert decision.category == "Access & Permissions"
    assert not decision.requires_review
    assert decision.confidence >= 0.7
    assert any(item["type"] == "category_keyword" for item in decision.evidence)


def test_no_match_routes_to_review():
    decision = classify(command("Please help me with this unusual thing."))
    assert decision.requires_review
    assert decision.category is None


def test_conflicting_categories_require_review():
    decision = classify(command("Need laptop and payroll assistance."))
    assert decision.requires_review


def test_risk_escalates_priority_but_conflict_stays_in_review():
    decision = classify(command("Security breach in data report export.", "Low"))
    assert decision.priority == Priority.HIGH.value
    assert decision.requires_review

