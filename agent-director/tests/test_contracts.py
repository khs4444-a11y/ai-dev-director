"""Contract-level checks only; these do not claim runtime isolation."""

import json
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.adapters.base import BaseCLIAdapter
from src.core.schema import TaskSpec
from src.pipeline.states import StateMachine
from src.safety.guard_interface import ScopeGuard


def task_payload():
    return dict(
        task_id=str(uuid4()),
        objective="Regression",
        repository="/repo",
        base_commit="a" * 40,
        allowed_paths=["src/**"],
        acceptance_criteria=["empty input fails"],
        test_commands=[dict(argv=["python", "-m", "pytest"])],
    )


def test_wire_roundtrip_and_zero_budget():
    task = TaskSpec(**task_payload(), max_changed_files=0)
    assert TaskSpec.model_validate_json(task.model_dump_json()) == task
    assert task.max_changed_files == 0


@pytest.mark.parametrize(
    "override",
    [
        dict(extra=True),
        dict(base_commit="HEAD"),
        dict(max_changed_files=-1),
        dict(test_commands=[]),
    ],
)
def test_invalid_task_rejected(override):
    with pytest.raises(ValidationError):
        TaskSpec(**(task_payload() | override))


@pytest.mark.parametrize("contract", [BaseCLIAdapter, StateMachine, ScopeGuard])
def test_contract_is_abstract(contract):
    with pytest.raises(TypeError):
        contract()


def test_generated_schema_matches():
    root = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, str(root / "scripts/export_schemas.py"), "--check"], check=True)
    schema = json.loads((root / "schemas/TaskSpec.schema.json").read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
