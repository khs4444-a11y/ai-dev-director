"""Enforcement contracts; declarations do not provide a security sandbox."""

from abc import ABC, abstractmethod
from pathlib import Path

from src.core.schema import GuardDecision, TaskSpec


class ScopeGuard(ABC):
    @abstractmethod
    def preflight(self, task: TaskSpec, worktree: Path) -> GuardDecision: ...

    @abstractmethod
    def inspect_patch(self, task: TaskSpec, worktree: Path, patch: bytes) -> GuardDecision: ...

    @abstractmethod
    def inspect_worktree(self, task: TaskSpec, worktree: Path) -> GuardDecision:
        """Check tracked/untracked/deleted/binary files, renames and symlink targets."""
        ...

    @abstractmethod
    def authorize_command(
        self, task: TaskSpec, argv: tuple[str, ...], cwd: Path
    ) -> GuardDecision: ...
