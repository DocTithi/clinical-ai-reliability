from __future__ import annotations

from .models import ReliabilityEnvelope


def render_markdown(envelope: ReliabilityEnvelope) -> str:
    m = envelope.metrics

    def fmt(value):
        return "N/A" if value is None else f"{value:.0%}"

    lines = [
        "# Clinical AI Reliability Report",
        "",
        f"- Run ID: `{envelope.run_id}`",
        f"- Protocol: `{envelope.protocol_version}`",
        f"- Status: **{envelope.protocol_status.value}**",
        "",
        "## Metrics",
        "",
        f"- Evidence linkage: {fmt(m.get('evidence_linkage'))}",
        f"- Support rate: {fmt(m.get('support_rate'))}",
        f"- Evidence freshness: {fmt(m.get('evidence_freshness'))}",
        f"- Counterfactual consistency: {fmt(m.get('counterfactual_consistency'))}",
        f"- Uncertainty coverage: {fmt(m.get('uncertainty_coverage'))}",
        f"- Protocol completeness: {fmt(m.get('protocol_completeness'))}",
        "",
        "## Flags",
        "",
    ]
    lines.extend(f"- `{flag}`" for flag in envelope.flags) if envelope.flags else lines.append("- None")
    lines += [
        "",
        "## Interpretation note",
        "",
        "These metrics describe CAR protocol checks. They are not a diagnosis, medical safety certification, regulatory approval, or clinical accuracy score.",
        "",
    ]
    return "\n".join(lines)
