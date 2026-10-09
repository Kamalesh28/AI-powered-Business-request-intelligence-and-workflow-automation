from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from .domain import Decision, ProcessingMode, Status
from .ollama import OllamaAdapter
from .rules import classify
from .storage import Repository
from .validation import validate_decision, validate_intake, validate_review


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


class RequestService:
    def __init__(self, repository: Repository):
        self.repository = repository

    def submit_and_process(self, payload: dict[str, object], request_id: str | None = None, processing_mode: str = ProcessingMode.RULE_BASED.value, ollama: OllamaAdapter | None = None) -> tuple[str, Decision]:
        command = validate_intake(payload)
        if processing_mode not in {mode.value for mode in ProcessingMode}:
            raise ValueError("Unsupported processing mode.")
        request_id = request_id or str(uuid4())
        self.repository.insert_request({
            "request_id": request_id, "title": command.title, "description": command.description,
            "department": command.department, "channel": command.channel,
            "declared_urgency": command.declared_urgency, "submitted_at_utc": utcnow(),
            "status": Status.SUBMITTED.value, "is_synthetic": 1,
        })
        decision = classify(command)
        validate_decision(decision)
        self._record_run(request_id, decision, ProcessingMode.RULE_BASED)
        final_decision = decision
        if processing_mode == ProcessingMode.OLLAMA_LOCAL.value:
            if ollama is None:
                raise ValueError("Ollama mode requires an Ollama adapter.")
            result = ollama.classify(command)
            if result.decision is None:
                self._record_invalid_ollama_run(request_id, result.model, result.raw_output, result.error or "Unknown local AI error")
            else:
                final_decision = result.decision
                self._record_run(request_id, final_decision, ProcessingMode.OLLAMA_LOCAL, raw_output=result.raw_output)
        self.repository.update_status(request_id, Status.NEEDS_REVIEW.value if final_decision.requires_review else Status.CLASSIFIED.value)
        return request_id, final_decision

    def _record_run(self, request_id: str, decision: Decision, mode: ProcessingMode, raw_output: str | None = None) -> str:
        run_id = str(uuid4())
        self.repository.insert_run({
            "processing_run_id": run_id, "request_id": request_id, "processing_mode": mode.value,
            "processed_at_utc": utcnow(), "engine_version": decision.engine_version,
            "proposed_category": decision.category, "proposed_priority": decision.priority,
            "confidence": decision.confidence, "evidence": decision.evidence, "raw_output_json": raw_output,
            "validation_status": "valid", "error_message": None,
        })
        return run_id

    def _record_invalid_ollama_run(self, request_id: str, model: str, raw_output: str | None, error: str) -> None:
        self.repository.insert_run({
            "processing_run_id": str(uuid4()), "request_id": request_id, "processing_mode": ProcessingMode.OLLAMA_LOCAL.value,
            "processed_at_utc": utcnow(), "engine_version": f"ollama:{model}", "proposed_category": None,
            "proposed_priority": None, "confidence": 0.0, "evidence": [{"type": "ollama_failure", "value": error}],
            "raw_output_json": raw_output, "validation_status": "invalid", "error_message": error,
        })


class ReviewService:
    def __init__(self, repository: Repository):
        self.repository = repository

    def review(self, request_id: str, processing_run_id: str, reviewer_name: object, category: object, priority: object, rationale: object, proposed_category: str | None, proposed_priority: str | None) -> None:
        reviewer, final_category, final_priority, rationale_text = validate_review(reviewer_name, category, priority, rationale)
        self.repository.insert_review({
            "review_id": str(uuid4()), "request_id": request_id, "processing_run_id": processing_run_id,
            "reviewer_name": reviewer, "reviewed_at_utc": utcnow(), "final_category": final_category,
            "final_priority": final_priority, "category_corrected": int(final_category != proposed_category),
            "priority_corrected": int(final_priority != proposed_priority), "rationale": rationale_text,
        })
        self.repository.update_status(request_id, Status.REVIEWED.value)
