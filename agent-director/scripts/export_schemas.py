"""Export normative schemas or fail on drift; run from any directory."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.core.schema import (  # noqa: E402
    AgentRequest,
    AgentResponse,
    GateResult,
    GuardDecision,
    TaskSpec,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for model in (TaskSpec, AgentRequest, AgentResponse, GateResult, GuardDecision):
        path = ROOT / "schemas" / f"{model.__name__}.schema.json"
        expected = json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2) + "\n"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                raise SystemExit(f"Schema drift: {path.name}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")


if __name__ == "__main__":
    main()
