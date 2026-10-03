# Research and Validation Plan

This document describes the work required before CAR can make strong scientific claims.

## Research question

Can a common, model-agnostic Reliability Envelope improve reproducibility, auditability, and failure discovery when evaluating heterogeneous clinical AI systems?

## Phase 1: protocol feasibility

Goals:

1. demonstrate that the same envelope can represent outputs from several model classes,
2. test deterministic serialization and provenance,
3. evaluate whether independent reviewers can interpret the fields consistently,
4. identify missing reliability signals.

Use only public or synthetic data for the initial release.

## Phase 2: counterfactual benchmark

Create a benchmark of clinically meaningful perturbations with expert-defined expected relations.

Candidate perturbation categories include demographic variables when clinically relevant, medication or allergy state, laboratory thresholds, temporal context, and presence or absence of red-flag features.

The benchmark must not assume that every demographic change ought to change an answer. Expected relations must be explicitly justified.

Primary metric: agreement between expected and observed relation.

Secondary analyses: model-to-model variation, failure categories, and reproducibility across seeds or temperatures where applicable.

## Phase 3: evidence verification study

Compare several ways of generating `support_assessment`:

- human adjudication,
- retrieval plus rule-based verification,
- retrieval plus model-based verification,
- hybrid adjudication.

Measure agreement, false support, missed support, citation correctness, and sensitivity to outdated or superseded evidence.

## Phase 4: external validation

Before claims of clinical utility:

- recruit independent domain experts,
- preregister the evaluation plan,
- publish benchmark construction rules,
- report inter-rater agreement,
- report confidence intervals,
- disclose model and prompt versions,
- invite independent replication.

## What would count as meaningful contribution

The project should earn credibility from evidence, not labels such as "breakthrough" or "world first."

Strong evidence would include reproducible discovery of failure modes missed by standard accuracy metrics, external use by independent research groups, measurable improvement in audit completeness, a validated counterfactual benchmark, interoperability with established health-data standards, and independently replicated results.

## Publication hygiene

Any manuscript should distinguish protocol design, implementation, benchmark results, clinical interpretation, and limitations.

No affiliation should be listed unless the author is entitled to use it.
