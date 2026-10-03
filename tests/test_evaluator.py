from datetime import date
import pytest
from clinical_ai_reliability import Policy, evaluate_run


def base_spec():
    return {
        "model": {"name": "demo", "version": "1"},
        "input_text": "synthetic input",
        "output_text": "synthetic output",
        "claims": [{"id": "c1", "text": "synthetic claim", "evidence_ids": ["e1"], "support_assessment": "supported", "uncertainty": 0.1}],
        "evidence": [{"id": "e1", "title": "synthetic evidence", "published_at": "2026-01-01", "superseded": False}],
        "counterfactuals": [{"id": "cf1", "description": "synthetic perturbation", "expected_relation": "same", "observed_relation": "same"}],
    }


def test_complete_low_risk_run():
    envelope = evaluate_run(base_spec(), today=date(2026, 10, 3))
    assert envelope.protocol_status.value == "protocol_complete"
    assert envelope.metrics["evidence_linkage"] == 1.0
    assert envelope.metrics["support_rate"] == 1.0
    assert envelope.metrics["counterfactual_consistency"] == 1.0
    assert envelope.provenance["raw_input_stored"] is False


def test_high_stakes_requires_review():
    spec = base_spec(); spec["claims"][0]["high_stakes"] = True
    envelope = evaluate_run(spec, today=date(2026, 10, 3))
    assert envelope.protocol_status.value == "review_required"
    assert "high_stakes_claim" in envelope.flags


def test_unsupported_claim_requires_review():
    spec = base_spec(); spec["claims"][0]["support_assessment"] = "unsupported"
    envelope = evaluate_run(spec, today=date(2026, 10, 3))
    assert "unsupported_claim" in envelope.flags


def test_failed_counterfactual_requires_review():
    spec = base_spec(); spec["counterfactuals"][0]["observed_relation"] = "change"
    envelope = evaluate_run(spec, today=date(2026, 10, 3))
    assert envelope.metrics["counterfactual_consistency"] == 0.0
    assert "counterfactual_failure" in envelope.flags


def test_missing_evidence_reference_requires_review():
    spec = base_spec(); spec["claims"][0]["evidence_ids"] = ["missing"]
    envelope = evaluate_run(spec, today=date(2026, 10, 3))
    assert "missing_evidence_reference" in envelope.flags


def test_stale_evidence_recommends_review():
    spec = base_spec(); spec["evidence"][0]["published_at"] = "2010-01-01"
    envelope = evaluate_run(spec, today=date(2026, 10, 3), policy=Policy(max_evidence_age_days=365 * 5))
    assert envelope.metrics["evidence_freshness"] == 0.0
    assert "stale_evidence" in envelope.flags
    assert envelope.protocol_status.value == "review_recommended"


def test_invalid_uncertainty_rejected():
    spec = base_spec(); spec["claims"][0]["uncertainty"] = 2.0
    with pytest.raises(ValueError):
        evaluate_run(spec, today=date(2026, 10, 3))


def test_run_id_is_stable_for_same_material():
    a = evaluate_run(base_spec(), today=date(2026, 10, 3))
    b = evaluate_run(base_spec(), today=date(2026, 10, 3))
    assert a.run_id == b.run_id
