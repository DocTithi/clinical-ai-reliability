# Clinical AI Reliability

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23127294.svg)](https://doi.org/10.5281/zenodo.23127294)

**Clinical AI Reliability (CAR)** is an experimental, open-source framework for producing a structured **Reliability Envelope** around outputs from medical and health AI systems.

Instead of treating a model response as a standalone answer, CAR records the information needed to inspect it: claim-level evidence links, evidence freshness, uncertainty declarations, counterfactual test results, contradictions, provenance, and human-review triggers.

> **Status:** early research software, v0.1.1.

## Why this project exists

Medical AI systems can produce fluent answers without making it easy to answer questions such as:

- Which clinical claims are linked to supporting evidence?
- Is the supporting evidence current or superseded?
- Did a clinically meaningful change in the input produce the expected change in output?
- What model, version, input, and output produced this result?
- Can the run be audited without retaining raw patient text?
- When should the output be escalated for human review?

CAR is designed as a model-agnostic reliability layer around research models, LLM pipelines, decision-support prototypes, and evaluation systems.

## Core idea: the Reliability Envelope

A CAR run produces a versioned, machine-readable record:

```json
{
  "protocol_version": "0.1.0",
  "run_id": "car_...",
  "protocol_status": "review_required",
  "metrics": {
    "evidence_linkage": 1.0,
    "support_rate": 0.5,
    "evidence_freshness": 1.0,
    "counterfactual_consistency": 1.0,
    "protocol_completeness": 0.92
  },
  "flags": ["unsupported_claim", "human_review_required"],
  "provenance": {
    "model_name": "example-model",
    "model_version": "1.0",
    "input_sha256": "...",
    "output_sha256": "..."
  }
}
```

**Protocol completeness is not a medical safety score, diagnostic accuracy score, or regulatory certification.** It only describes how completely a run supplies the information expected by the configured CAR protocol.

## Design principles

1. **Model agnostic**: usable with LLMs, classifiers, multimodal systems, and custom pipelines.
2. **Claim level**: reliability information is attached to individual clinical claims.
3. **Evidence aware**: evidence can be linked, aged, and marked as superseded.
4. **Counterfactual testing**: clinically meaningful perturbations can be checked against an expected relation.
5. **Privacy first**: provenance can use hashes instead of storing raw patient text.
6. **Human review by design**: configured conditions can explicitly trigger review.
7. **Versioned protocol**: the Reliability Envelope has a schema that can evolve without silently changing meaning.

## Installation for development

```bash
git clone https://github.com/DocTithi/clinical-ai-reliability.git
cd clinical-ai-reliability
python -m pip install -e ".[dev]"
```

## Quick start

```python
from clinical_ai_reliability import evaluate_run

spec = {
    "model": {"name": "demo-model", "version": "1.0"},
    "input_text": "Synthetic patient example",
    "output_text": "The model generated a clinical claim.",
    "claims": [
        {
            "id": "c1",
            "text": "Example clinical claim.",
            "evidence_ids": ["e1"],
            "support_assessment": "supported",
            "uncertainty": 0.10,
            "high_stakes": True
        }
    ],
    "evidence": [
        {
            "id": "e1",
            "title": "Example guideline",
            "published_at": "2026-01-01",
            "superseded": False
        }
    ]
}

envelope = evaluate_run(spec)
print(envelope.to_json())
```

## CLI

```bash
car-evaluate examples/synthetic_case.json
car-evaluate examples/synthetic_case.json --output reliability-envelope.json
```

## Important scope

CAR does **not** diagnose patients, prescribe treatment, replace clinical judgment, or certify a model as safe. It is research infrastructure for making AI evaluation more explicit, reproducible, and auditable.

A `support_assessment` in v0.1.0 is an **evaluation input**, not an assertion made by CAR itself. Future verifier adapters can generate these assessments from external evidence-retrieval or adjudication systems.

All examples in this repository use synthetic data.

## Research direction

The long-term research goal is to test whether a common Reliability Envelope can make heterogeneous clinical AI systems easier to compare, audit, reproduce, and route for human review.

See [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md) and [docs/PROTOCOL.md](docs/PROTOCOL.md).

## Author

**Sabrina Chowdhury Tithi**

No institutional affiliation is asserted by this repository.

## License

Apache License 2.0.
