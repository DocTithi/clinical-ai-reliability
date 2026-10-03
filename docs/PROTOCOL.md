# CAR Protocol v0.1

The Clinical AI Reliability (CAR) protocol defines a common envelope for reliability signals around a medical or health AI output.

## What CAR v0.1 measures

- **Evidence linkage**: fraction of declared claims that reference at least one evidence record.
- **Support rate**: fraction of claims whose supplied support assessment is `supported`.
- **Uncertainty coverage**: fraction of claims with a normalized uncertainty declaration.
- **Evidence freshness**: fraction of date-assessable, used evidence that is not superseded and is within the configured age window.
- **Counterfactual consistency**: fraction of assessable perturbation tests in which observed and expected relations match.
- **Protocol completeness**: fraction of protocol information categories available for evaluation.

## Why there is no medical safety score

A single percentage can be mistaken for clinical safety, model accuracy, or regulatory approval. CAR therefore exposes component metrics and a protocol status.

`protocol_complete`, `review_recommended`, and `review_required` are workflow states produced by a configured policy. They are not clinical verdicts.

## Claim-level evidence

Each claim has an ID and may reference evidence IDs. CAR does not assume that a citation proves a claim.

The field `support_assessment` is deliberately an input to the protocol. It may come from blinded human adjudication, a retrieval-and-verification system, a validated task-specific verifier, or another research pipeline.

This separation lets future verifier modules improve without changing the envelope format.

## Counterfactual tests

A counterfactual observation includes the perturbation description, an expected relation (`same`, `change`, or `unknown`), an observed relation, and optional rationale.

CAR v0.1 does not attempt to judge semantic equivalence between arbitrary clinical texts. That relation must be supplied by an evaluator or adapter. This avoids pretending that naive string matching is a valid clinical consistency test.

## Provenance and privacy

The default provenance record stores SHA-256 hashes of input, output, prompt, and model metadata. Raw clinical text is not copied into the envelope by default.

Hashing is not anonymization and should not be treated as a complete privacy control. Deployments remain responsible for privacy, security, consent, access control, and applicable law.

## Human review policy

The default policy is conservative:

- high-stakes claim: review required,
- unsupported claim: review required,
- contradiction: review required,
- failed counterfactual test: review required,
- uncertainty above threshold: review required,
- incomplete or stale information: review recommended.

Projects can instantiate a custom `Policy`, but should document and validate changes.
