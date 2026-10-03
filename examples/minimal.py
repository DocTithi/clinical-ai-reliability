from clinical_ai_reliability import evaluate_run

spec = {
    "model": {"name": "demo", "version": "1"},
    "input_text": "Synthetic input",
    "output_text": "Synthetic output",
    "claims": [
        {
            "id": "c1",
            "text": "Synthetic claim",
            "evidence_ids": ["e1"],
            "support_assessment": "supported",
            "uncertainty": 0.10,
        }
    ],
    "evidence": [
        {"id": "e1", "title": "Synthetic evidence", "published_at": "2026-01-01"}
    ],
}

print(evaluate_run(spec).to_json())
