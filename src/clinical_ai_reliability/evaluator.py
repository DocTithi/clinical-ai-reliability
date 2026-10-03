from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime, timezone
import hashlib
from typing import Any

from .counterfactual import counterfactual_consistency
from .freshness import evidence_freshness_score
from .models import Claim, CounterfactualObservation, Evidence, Policy, ProtocolStatus, Relation, ReliabilityEnvelope, SupportAssessment
from .provenance import build_provenance

PROTOCOL_VERSION = "0.1.0"


def _clamp_probability(value: float | None, *, field_name: str) -> float | None:
    if value is None:
        return None
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{field_name} must be between 0 and 1")
    return value


def _parse_claim(item: dict[str, Any]) -> Claim:
    return Claim(
        id=str(item["id"]),
        text=str(item["text"]),
        evidence_ids=tuple(str(x) for x in item.get("evidence_ids", [])),
        support_assessment=SupportAssessment(item.get("support_assessment", "unknown")),
        uncertainty=_clamp_probability(item.get("uncertainty"), field_name="uncertainty"),
        high_stakes=bool(item.get("high_stakes", False)),
        contradictions=tuple(str(x) for x in item.get("contradictions", [])),
        requires_review=bool(item.get("requires_review", False)),
        metadata=dict(item.get("metadata", {})),
    )


def _parse_evidence(item: dict[str, Any]) -> Evidence:
    return Evidence(
        id=str(item["id"]),
        title=str(item["title"]),
        published_at=item.get("published_at"),
        reviewed_at=item.get("reviewed_at"),
        source_type=item.get("source_type"),
        url=item.get("url"),
        superseded=bool(item.get("superseded", False)),
        metadata=dict(item.get("metadata", {})),
    )


def _parse_counterfactual(item: dict[str, Any]) -> CounterfactualObservation:
    return CounterfactualObservation(
        id=str(item["id"]),
        description=str(item["description"]),
        expected_relation=Relation(item.get("expected_relation", "unknown")),
        observed_relation=Relation(item.get("observed_relation", "unknown")),
        rationale=item.get("rationale"),
        metadata=dict(item.get("metadata", {})),
    )


def _safe_ratio(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def _serialize_claim(claim: Claim) -> dict[str, Any]:
    value = asdict(claim)
    value["support_assessment"] = claim.support_assessment.value
    value["evidence_ids"] = list(claim.evidence_ids)
    value["contradictions"] = list(claim.contradictions)
    return value


def _serialize_counterfactual(item: CounterfactualObservation) -> dict[str, Any]:
    value = asdict(item)
    value["expected_relation"] = item.expected_relation.value
    value["observed_relation"] = item.observed_relation.value
    value["passes"] = item.passes
    return value


def evaluate_run(spec: dict[str, Any], *, policy: Policy | None = None, today: date | None = None) -> ReliabilityEnvelope:
    """Evaluate supplied reliability signals and return a Reliability Envelope.

    CAR does not itself assert clinical truth in v0.1. Evidence-support assessments
    and counterfactual relations are supplied by evaluators, adapters, or humans.
    """
    policy = policy or Policy()
    today = today or datetime.now(timezone.utc).date()

    model = dict(spec.get("model", {}))
    if not model.get("name"):
        raise ValueError("model.name is required")
    if not model.get("version"):
        raise ValueError("model.version is required")

    input_text = str(spec.get("input_text", ""))
    output_text = str(spec.get("output_text", ""))
    if not output_text:
        raise ValueError("output_text is required")

    claims = [_parse_claim(x) for x in spec.get("claims", [])]
    evidence = [_parse_evidence(x) for x in spec.get("evidence", [])]
    counterfactuals = [_parse_counterfactual(x) for x in spec.get("counterfactuals", [])]

    evidence_by_id = {item.id: item for item in evidence}
    if len(evidence_by_id) != len(evidence):
        raise ValueError("Evidence IDs must be unique")
    if len({claim.id for claim in claims}) != len(claims):
        raise ValueError("Claim IDs must be unique")

    missing_refs: dict[str, list[str]] = {}
    used_evidence_ids: set[str] = set()
    for claim in claims:
        absent = [eid for eid in claim.evidence_ids if eid not in evidence_by_id]
        if absent:
            missing_refs[claim.id] = absent
        used_evidence_ids.update(eid for eid in claim.evidence_ids if eid in evidence_by_id)

    used_evidence = [evidence_by_id[eid] for eid in sorted(used_evidence_ids)]

    evidence_linkage = _safe_ratio(sum(bool(c.evidence_ids) for c in claims), len(claims))
    support_rate = _safe_ratio(sum(c.support_assessment is SupportAssessment.SUPPORTED for c in claims), len(claims))
    uncertainty_coverage = _safe_ratio(sum(c.uncertainty is not None for c in claims), len(claims))
    freshness, freshness_known_fraction = evidence_freshness_score(used_evidence, today=today, max_age_days=policy.max_evidence_age_days)
    cf_score, cf_known_fraction = counterfactual_consistency(counterfactuals)

    checks = [
        evidence_linkage is not None,
        support_rate is not None,
        uncertainty_coverage is not None,
        freshness is not None,
        cf_score is not None,
        bool(model.get("version")),
        bool(input_text),
        bool(output_text),
    ]
    protocol_completeness = sum(checks) / len(checks)

    flags: list[str] = []
    require_review = False
    recommend_review = False

    if missing_refs:
        flags.append("missing_evidence_reference")
        require_review = True
    if any(not c.evidence_ids for c in claims):
        flags.append("claim_without_evidence")
        recommend_review = True
    if any(c.support_assessment is SupportAssessment.UNSUPPORTED for c in claims):
        flags.append("unsupported_claim")
        require_review = require_review or policy.unsupported_requires_review
    if any(c.support_assessment is SupportAssessment.PARTIAL for c in claims):
        flags.append("partially_supported_claim")
        recommend_review = True
    if any(c.support_assessment is SupportAssessment.UNKNOWN for c in claims):
        flags.append("support_unknown")
        recommend_review = True
    if any(c.contradictions for c in claims):
        flags.append("contradiction_present")
        require_review = require_review or policy.contradiction_requires_review
    if any(c.high_stakes for c in claims):
        flags.append("high_stakes_claim")
        require_review = require_review or policy.high_stakes_requires_review
    if any(c.requires_review for c in claims):
        flags.append("explicit_review_request")
        require_review = True

    uncertainties = [c.uncertainty for c in claims if c.uncertainty is not None]
    if policy.require_uncertainty and claims and len(uncertainties) != len(claims):
        flags.append("uncertainty_missing")
        recommend_review = True
    if any(value > policy.max_uncertainty for value in uncertainties):
        flags.append("uncertainty_above_policy_threshold")
        require_review = True

    if any(item.superseded for item in used_evidence):
        flags.append("superseded_evidence")
        recommend_review = True
    if freshness is not None and freshness < 1.0:
        flags.append("stale_evidence")
        recommend_review = True
    if used_evidence and freshness_known_fraction < 1.0:
        flags.append("evidence_date_unknown")
        recommend_review = True

    if any(item.passes is False for item in counterfactuals):
        flags.append("counterfactual_failure")
        require_review = require_review or policy.counterfactual_failure_requires_review
    if counterfactuals and cf_known_fraction < 1.0:
        flags.append("counterfactual_relation_unknown")
        recommend_review = True

    if require_review:
        status = ProtocolStatus.REVIEW_REQUIRED
        flags.append("human_review_required")
    elif recommend_review:
        status = ProtocolStatus.REVIEW_RECOMMENDED
    else:
        status = ProtocolStatus.COMPLETE

    provenance = build_provenance(model=model, input_text=input_text, output_text=output_text, prompt=spec.get("prompt"))
    run_material = PROTOCOL_VERSION + provenance["model_metadata_sha256"] + provenance["input_sha256"] + provenance["output_sha256"]
    run_id = "car_" + hashlib.sha256(run_material.encode("utf-8")).hexdigest()[:16]

    metrics = {
        "evidence_linkage": evidence_linkage,
        "support_rate": support_rate,
        "uncertainty_coverage": uncertainty_coverage,
        "evidence_freshness": freshness,
        "evidence_freshness_assessable_fraction": freshness_known_fraction,
        "counterfactual_consistency": cf_score,
        "counterfactual_assessable_fraction": cf_known_fraction,
        "protocol_completeness": protocol_completeness,
    }

    return ReliabilityEnvelope(
        protocol_version=PROTOCOL_VERSION,
        run_id=run_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        protocol_status=status,
        metrics=metrics,
        flags=sorted(set(flags)),
        claims=[_serialize_claim(x) for x in claims],
        evidence=[asdict(x) for x in evidence],
        counterfactuals=[_serialize_counterfactual(x) for x in counterfactuals],
        provenance=provenance,
        policy=asdict(policy),
    )
