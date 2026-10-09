from __future__ import annotations

from .services import RequestService, ReviewService
from .storage import Repository

SAMPLES = (
    {"id": "seed-001", "title": "VPN access for new analyst", "description": "Please provide VPN permission and MFA access for a new analyst.", "department": "IT", "channel": "Portal", "declared_urgency": "Normal"},
    {"id": "seed-002", "title": "Invoice report needed", "description": "Need a dashboard export of unpaid vendor invoice data.", "department": "Finance", "channel": "Email", "declared_urgency": "High"},
    {"id": "seed-003", "title": "Possible data breach", "description": "We saw a possible security incident and data breach in a reporting export.", "department": "Legal", "channel": "Phone", "declared_urgency": "Critical"},
    {"id": "seed-004", "title": "Need help", "description": "Can someone point me in the right direction for this request?", "department": "Operations", "channel": "Portal", "declared_urgency": "Not specified"},
    {"id": "seed-005", "title": "Payroll leave balance", "description": "The payroll leave balance for an employee looks incorrect.", "department": "Human Resources", "channel": "Email", "declared_urgency": "Normal"},
    {"id": "seed-006", "title": "New vendor purchase order", "description": "Please create a purchase order for a new office equipment vendor.", "department": "Finance", "channel": "Portal", "declared_urgency": "Low"},
)


def seed(repository: Repository) -> int:
    service = RequestService(repository)
    review_service = ReviewService(repository)
    created = 0
    for item in SAMPLES:
        if repository.has_request(item["id"]):
            continue
        payload = {key: value for key, value in item.items() if key != "id"}
        # Preserve fixed IDs for repeatable, inspectable synthetic seed data.
        service.submit_and_process(payload, request_id=item["id"])
        created += 1
    # Include one recorded synthetic correction so the dashboard has an auditable review example.
    for queued in repository.requests_for_review():
        if queued["request_id"] == "seed-004":
            review_service.review(
                "seed-004", queued["processing_run_id"], "Demo Reviewer", "General Inquiry", "Normal",
                "Synthetic demonstration correction for an unclassified request.",
                queued["proposed_category"], queued["proposed_priority"],
            )
            break
    return created
