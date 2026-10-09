from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class Category(StrEnum):
    ACCESS = "Access & Permissions"
    DATA = "Data & Reporting"
    FINANCE = "Finance & Procurement"
    HR = "HR & People Operations"
    IT = "IT Support"
    COMPLIANCE = "Compliance & Risk"
    GENERAL = "General Inquiry"


class Priority(StrEnum):
    CRITICAL = "Critical"
    HIGH = "High"
    NORMAL = "Normal"
    LOW = "Low"


class Status(StrEnum):
    SUBMITTED = "submitted"
    CLASSIFIED = "classified"
    NEEDS_REVIEW = "needs_review"
    REVIEWED = "reviewed"


class ProcessingMode(StrEnum):
    RULE_BASED = "rule_based"
    OLLAMA_LOCAL = "ollama_local"


DEPARTMENTS = ("Finance", "Human Resources", "IT", "Operations", "Sales", "Legal")
CHANNELS = ("Portal", "Email", "Phone", "In person")
URGENCIES = ("Not specified", "Low", "Normal", "High", "Critical")


@dataclass(frozen=True)
class IntakeCommand:
    title: str
    description: str
    department: str
    channel: str
    declared_urgency: str


@dataclass(frozen=True)
class Decision:
    category: str | None
    priority: str | None
    confidence: float
    evidence: list[dict[str, Any]]
    requires_review: bool
    engine_version: str = "rules-v1"
