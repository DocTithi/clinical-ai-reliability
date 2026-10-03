from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .evaluator import evaluate_run
from .report import render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="car-evaluate", description="Create a Clinical AI Reliability Envelope from JSON.")
    parser.add_argument("input", type=Path, help="Path to run specification JSON.")
    parser.add_argument("-o", "--output", type=Path, help="Write JSON envelope to this path.")
    parser.add_argument("--markdown", type=Path, help="Optionally write a Markdown report.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        spec = json.loads(args.input.read_text(encoding="utf-8"))
        envelope = evaluate_run(spec)
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    payload = envelope.to_json()
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    if args.markdown:
        args.markdown.write_text(render_markdown(envelope) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
