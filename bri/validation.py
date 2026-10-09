from __future__ import annotations

from .domain import CHANNELS, DEPARTMENTS, URGENCIES, Category, Decision, IntakeCommand, Priority


class ValidationError(ValueError):
    def __init__(self, errors: dict[str, str]):
        self.errors = errors
        super().__init__("; ".join(errors.values()))


def _text(value: object, field: str, minimum: int, maximum: int) -> str:
    cleaned = str(value or "").strip()
    if len(cleaned) < minimum:
        raise ValueError(f"{field} is required.")
    if len(cleaned) > maximum:
        raise ValueError(f"{field} must be {maximum} characters or fewer.")
    return cleaned


def validate_intake(payload: dict[str, object]) -> IntakeCommand:
    errors: dict[str, str] = {}
    values: dict[str, str] = {}
    for key, label, low, high in (("title", "Title", 3, 120), ("description", "Description", 10, 4000)):
        try:
            values[key] = _text(payload.get(key), label, low, high)
        except ValueError as exc:
            errors[key] = str(exc)
    for key, allowed in (("department", DEPARTMENTS), ("channel", CHANNELS), ("declared_urgency", URGENCIES)):
        value = str(payload.get(key) or "").strip()
        if value not in allowed:
            errors[key] = f"Choose a supported {key.replace('_', ' ')}."
        else:
            values[key] = value
    if errors:
        raise ValidationError(errors)
    return IntakeCommand(**values)


def validate_decision(decision: Decision) -> None:
    errors: dict[str, str] = {}
    allowed_categories = {item.value for item in Category}
    allowed_priorities = {item.value for item in Priority}
    if decision.category is not None and decision.category not in allowed_categories:
        errors["category"] = "Decision category is not supported."
    if decision.priority is not None and decision.priority not in allowed_priorities:
        errors["priority"] = "Decision priority is not supported."
    if not isinstance(decision.confidence, (int, float)) or not 0 <= decision.confidence <= 1:
        errors["confidence"] = "Decision confidence must be between 0 and 1."
    if not isinstance(decision.evidence, list):
        errors["evidence"] = "Decision evidence must be a list."
    if not decision.requires_review and (decision.category is None or decision.priority is None):
        errors["decision"] = "Final automated decisions require category and priority."
    if errors:
        raise ValidationError(errors)


def validate_review(reviewer_name: object, category: object, priority: object, rationale: object) -> tuple[str, str, str, str]:
    errors: dict[str, str] = {}
    try:
        reviewer = _text(reviewer_name, "Reviewer name", 2, 100)
    except ValueError as exc:
        errors["reviewer_name"] = str(exc)
        reviewer = ""
    category_text = str(category or "").strip()
    priority_text = str(priority or "").strip()
    if category_text not in {item.value for item in Category}:
        errors["category"] = "Choose a supported category."
    if priority_text not in {item.value for item in Priority}:
        errors["priority"] = "Choose a supported priority."
    rationale_text = str(rationale or "").strip()
    if len(rationale_text) > 1000:
        errors["rationale"] = "Rationale must be 1000 characters or fewer."
    if errors:
        raise ValidationError(errors)
    return reviewer, category_text, priority_text, rationale_text
