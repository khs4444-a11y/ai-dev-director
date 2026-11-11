"""No vendor command flags are assumed by this interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from uuid import UUID

from src.core.schema import AgentRequest, AgentResponse, Provider


class BaseCLIAdapter(ABC):
    @property
    @abstractmethod
    def provider(self) -> Provider: ...

    @abstractmethod
    async def probe(self, executable: Path) -> bool:
        """Check executable, installed version, authentication and headless capability."""
        ...

    @abstractmethod
    def build_argv(self, request: AgentRequest) -> tuple[str, ...]: ...

    @abstractmethod
    async def invoke(self, request: AgentRequest) -> AgentResponse:
        """Execute through shared isolated supervisor; never shell=True."""
        ...

    @abstractmethod
    def parse_output(
        self, request: AgentRequest, stdout: bytes, stderr: bytes, exit_code: int
    ) -> AgentResponse: ...

    @abstractmethod
    async def cancel(self, request_id: UUID) -> None:
        """Idempotently request supervisor termination of the entire process tree."""
        ...
