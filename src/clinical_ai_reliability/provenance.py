from __future__ import annotations

import hashlib
import json
from typing import Any


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_text(payload)


def build_provenance(*, model: dict[str, Any], input_text: str, output_text: str, prompt: str | None = None) -> dict[str, Any]:
    """Create privacy-minimizing provenance without retaining raw input/output text."""
    return {
        "model_name": str(model.get("name", "unknown")),
        "model_version": str(model.get("version", "unknown")),
        "model_provider": model.get("provider"),
        "input_sha256": sha256_text(input_text),
        "output_sha256": sha256_text(output_text),
        "prompt_sha256": sha256_text(prompt) if prompt is not None else None,
        "model_metadata_sha256": canonical_sha256(model),
        "raw_input_stored": False,
        "raw_output_stored": False,
    }
