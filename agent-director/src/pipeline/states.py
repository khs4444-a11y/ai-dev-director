"""Normative state vocabulary; transition execution is intentionally absent."""

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.schema import GateResult, TaskSpec


class PipelineState(StrEnum):
    CREATED = "created"
    PLANNED = "planned"
    RED = "red"
    GREEN = "green"
    REFACTORED = "refactored"
    VERIFIED = "verified"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Gate(StrEnum):
    PLAN = "plan"
    RED = "red"
    GREEN = "green"
    REFACTOR = "refactor"
    VERIFY = "verify"


class StateMachine(ABC):
    @abstractmethod
    def transition(
        self,
        task: "TaskSpec",
        current: PipelineState,
        target: PipelineState,
        evidence: "GateResult",
    ) -> PipelineState:
        """Validate task, gate, attempt, commit and current state before atomic CAS."""
        ...
