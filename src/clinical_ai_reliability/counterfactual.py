from __future__ import annotations

from .models import CounterfactualObservation


def counterfactual_consistency(observations: list[CounterfactualObservation]) -> tuple[float | None, float]:
    """Return (consistency score, assessable fraction).

    v0.1 intentionally does not pretend exact string matching is a valid clinical
    semantic test. An external evaluator or human supplies the observed relation.
    """
    if not observations:
        return None, 0.0
    outcomes = [item.passes for item in observations]
    assessable = [x for x in outcomes if x is not None]
    if not assessable:
        return None, 0.0
    return sum(bool(x) for x in assessable) / len(assessable), len(assessable) / len(observations)
