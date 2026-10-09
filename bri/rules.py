from __future__ import annotations

import re

from .domain import Category, Decision, IntakeCommand, Priority

RULE_VERSION = "rules-v1"
CONFIDENCE_THRESHOLD = 0.70

CATEGORY_RULES: dict[Category, tuple[str, ...]] = {
    Category.ACCESS: ("access", "permission", "login", "password", "account", "mfa"),
    Category.DATA: ("report", "dashboard", "data", "metric", "export", "analytics"),
    Category.FINANCE: ("invoice", "purchase order", "procurement", "budget", "vendor", "payment"),
    Category.HR: ("payroll", "leave", "onboarding", "benefits", "employee", "recruiting"),
    Category.IT: ("laptop", "vpn", "software", "printer", "network", "computer"),
    Category.COMPLIANCE: ("compliance", "audit", "privacy", "breach", "legal", "policy"),
}
HIGH_RISK = ("breach", "security incident", "outage", "fraud", "data loss")
PRIORITY_ORDER = {Priority.LOW: 1, Priority.NORMAL: 2, Priority.HIGH: 3, Priority.CRITICAL: 4}


def _contains(text: str, phrase: str) -> bool:
    return bool(re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text))


def classify(command: IntakeCommand) -> Decision:
    text = f"{command.title} {command.description}".lower()
    evidence: list[dict[str, str]] = []
    matches: dict[Category, list[str]] = {}
    for category, terms in CATEGORY_RULES.items():
        hits = [term for term in terms if _contains(text, term)]
        if hits:
            matches[category] = hits
            evidence.append({"type": "category_keyword", "category": category.value, "terms": ", ".join(hits)})

    risk_hits = [term for term in HIGH_RISK if _contains(text, term)]
    if risk_hits:
        evidence.append({"type": "risk_keyword", "terms": ", ".join(risk_hits)})
    urgency = command.declared_urgency
    evidence.append({"type": "declared_urgency", "value": urgency})

    if not matches:
        return Decision(None, None, 0.0, evidence, True, RULE_VERSION)
    ranked = sorted(matches.items(), key=lambda item: (-len(item[1]), item[0].value))
    category, category_hits = ranked[0]
    conflict = len(ranked) > 1 and len(ranked[1][1]) == len(category_hits)
    confidence = min(0.95, 0.55 + 0.15 * len(category_hits))
    if len(matches) > 1:
        confidence -= 0.15
    confidence = max(0.0, round(confidence, 2))

    priority = Priority.NORMAL
    if urgency in (Priority.LOW.value, Priority.NORMAL.value, Priority.HIGH.value, Priority.CRITICAL.value):
        priority = Priority(urgency)
    if risk_hits and PRIORITY_ORDER[priority] < PRIORITY_ORDER[Priority.HIGH]:
        priority = Priority.HIGH
    if risk_hits:
        evidence.append({"type": "priority_escalation", "value": priority.value})

    requires_review = conflict or confidence < CONFIDENCE_THRESHOLD or (bool(risk_hits) and len(matches) > 1)
    if conflict:
        evidence.append({"type": "conflict", "value": "equally strong category matches"})
    return Decision(category.value, priority.value, confidence, evidence, requires_review, RULE_VERSION)

