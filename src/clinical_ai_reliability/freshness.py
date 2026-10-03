from __future__ import annotations

from datetime import date, datetime
from .models import Evidence


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"Expected YYYY-MM-DD date, got {value!r}") from exc


def evidence_is_fresh(evidence: Evidence, *, today: date, max_age_days: int) -> bool | None:
    if evidence.superseded:
        return False
    published = _parse_date(evidence.published_at)
    if published is None:
        return None
    age_days = (today - published).days
    if age_days < 0:
        return None
    return age_days <= max_age_days


def evidence_freshness_score(evidence: list[Evidence], *, today: date, max_age_days: int) -> tuple[float | None, float]:
    """Return (freshness among assessable evidence, assessable fraction)."""
    if not evidence:
        return None, 0.0
    results = [evidence_is_fresh(item, today=today, max_age_days=max_age_days) for item in evidence]
    assessable = [x for x in results if x is not None]
    if not assessable:
        return None, 0.0
    score = sum(bool(x) for x in assessable) / len(assessable)
    known_fraction = len(assessable) / len(results)
    return score, known_fraction
