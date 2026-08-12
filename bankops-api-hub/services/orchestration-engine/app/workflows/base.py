from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from shared.utils.logging import get_logger

logger = get_logger(__name__)


class StepStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepResult(BaseModel):
    step_name: str
    status: StepStatus
    output: dict[str, Any] = {}
    error: str | None = None


class WorkflowContext(BaseModel):
    workflow_id: str
    transaction_id: str
    correlation_id: str
    tenant_id: str
    payload: dict[str, Any]
    step_results: list[StepResult] = []
    metadata: dict[str, Any] = {}

    def add_result(self, result: StepResult) -> None:
        self.step_results.append(result)

    def last_output(self) -> dict[str, Any]:
        for r in reversed(self.step_results):
            if r.status == StepStatus.COMPLETED:
                return r.output
        return {}

    def has_failed(self) -> bool:
        return any(r.status == StepStatus.FAILED for r in self.step_results)


class WorkflowStep(ABC):
    name: str = "base_step"

    @abstractmethod
    async def execute(self, ctx: WorkflowContext) -> StepResult: ...

    @abstractmethod
    async def rollback(self, ctx: WorkflowContext) -> None: ...
