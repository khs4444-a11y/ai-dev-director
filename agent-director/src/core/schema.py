"""Pydantic v2 wire contracts. Runtime policy belongs to future guards."""

from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.pipeline.states import Gate


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["1.0"] = "1.0"


class Provider(StrEnum):
    CODEX = "codex"
    CLAUDE = "claude"
    GEMINI = "gemini"
    ANTIGRAVITY = "antigravity"


class Role(StrEnum):
    PLANNER = "planner"
    BUILDER = "builder"
    REVIEWER = "reviewer"


class CommandSpec(Contract):
    argv: list[str] = Field(min_length=1)
    timeout_seconds: int = Field(default=120, ge=1, le=3600)


class TaskSpec(Contract):
    task_id: UUID
    objective: str = Field(min_length=1)
    repository: str = Field(min_length=1)
    base_commit: str = Field(pattern=r"^[0-9a-f]{40}([0-9a-f]{24})?$")
    allowed_paths: list[str] = Field(min_length=1)
    acceptance_criteria: list[str] = Field(min_length=1)
    test_commands: list[CommandSpec] = Field(min_length=1)
    max_changed_files: int = Field(default=10, ge=0)
    max_changed_lines: int = Field(default=500, ge=0)
    max_attempts: int = Field(default=3, ge=1, le=10)


class AgentRequest(Contract):
    request_id: UUID
    task: TaskSpec
    role: Role
    gate: Gate
    attempt: int = Field(ge=1)
    worktree: str
    candidate_commit: str = Field(pattern=r"^[0-9a-f]{40}([0-9a-f]{24})?$")
    prompt: str = Field(min_length=1)


class Artifact(Contract):
    relative_path: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    kind: Literal["patch", "test_log", "review", "manifest"]


class AgentResponse(Contract):
    request_id: UUID
    provider: Provider
    status: Literal["ok", "timeout", "unavailable", "invalid_output", "error", "cancelled"]
    summary: str
    artifacts: list[Artifact] = Field(default_factory=list)
    exit_code: int | None = None
    elapsed_seconds: float = Field(ge=0)


class GateResult(Contract):
    task_id: UUID
    request_id: UUID
    gate: Gate
    attempt: int = Field(ge=1)
    candidate_commit: str = Field(pattern=r"^[0-9a-f]{40}([0-9a-f]{24})?$")
    outcome: Literal["pass", "fail", "blocked"]
    actor_role: Role
    actor_provider: Provider
    evidence: list[Artifact] = Field(min_length=1)
    reason: str = Field(min_length=1)


class GuardDecision(Contract):
    allowed: bool
    violations: list[str] = Field(default_factory=list)
    changed_files: int = Field(ge=0)
    changed_lines: int = Field(ge=0)
