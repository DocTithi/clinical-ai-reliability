import json
from pathlib import Path
import pytest
jsonschema = pytest.importorskip("jsonschema")
from clinical_ai_reliability import evaluate_run


def test_generated_envelope_matches_schema():
    spec = {"model": {"name": "demo", "version": "1"}, "input_text": "synthetic input", "output_text": "synthetic output", "claims": [], "evidence": []}
    envelope = evaluate_run(spec).to_dict()
    schema_path = Path(__file__).parents[1] / "schemas" / "reliability-envelope-v0.1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validate(envelope, schema)
