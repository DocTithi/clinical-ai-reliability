from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import json
from typing import Any


class SupportAssessment(str, Enum):
    SUPPORTED = "supported"
    PARTIAL = "partial"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


class Relation(str, Enum):
    SAME = "same"
    CHANGE = "change"
    UNKNOWN = "unknown"


class ProtocolStatus(str, Enum):
    COMPLETE = "protocol_complete"
    REVIEW_RECOMMENDED = "review_recommended"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class Evidence:
    id: str
    title: str
    published_at: str | None = None
    reviewed_at: str | None = None
    source_type: str | None = None
    url: str | None = None
    superseded: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Claim:
    id: str
    text: str
    evidence_ids: tuple[str, ...] = ()
    support_assessment: SupportAssessment = SupportAssessment.UNKNOWN
    uncertainty: float | None = None
    high_stakes: bool = False
    contradictions: tuple[str, ...] = ()
    requires_review: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CounterfactualObservation:
    id: str
    description: str
    expected_relation: Relation
    observed_relation: Relation
    rationale: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def passes(self) -> bool | None:
        if self.expected_relation is Relation.UNKNOWN or self.observed_relation is Relation.UNKNOWN:
            return None
        return self.expected_relation is self.observed_relation


@dataclass(frozen=True)
class Policy:
    max_evidence_age_days: int = 365 * 5
    max_uncertainty: float = 0.35
    require_uncertainty: bool = True
    high_stakes_requires_review: bool = True
    unsupported_requires_review: bool = True
    contradiction_requires_review: bool = True
    counterfactual_failure_requires_review: bool = True


@dataclass
class ReliabilityEnvelope:
    protocol_version: str
    run_id: str
    created_at: str
    protocol_status: ProtocolStatus
    metrics: dict[str, float | None]
    flags: list[str]
    claims: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    counterfactuals: list[dict[str, Any]]
    provenance: dict[str, Any]
    policy: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["protocol_status"] = self.protocol_status.value
        return data

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True, ensure_ascii=False)
