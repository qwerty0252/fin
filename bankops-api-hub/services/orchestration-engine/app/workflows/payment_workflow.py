import uuid
from typing import Any

from app.config import Settings
from app.workflows.base import StepStatus, WorkflowContext, WorkflowStep
from app.workflows.steps import (
    FraudCheckStep,
    NotificationStep,
    PaymentSubmissionStep,
    RoutingStep,
    ValidationStep,
)
from shared.utils.logging import get_logger

logger = get_logger(__name__)


class PaymentWorkflow:
    """
    Standard payment workflow:
    Validate → Fraud Check → Route → Submit → Notify
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._steps: list[WorkflowStep] = [
            ValidationStep(),
            FraudCheckStep(),
            RoutingStep(settings),
            PaymentSubmissionStep(settings),
            NotificationStep(settings),
        ]

    async def execute(
        self,
        transaction_id: str,
        correlation_id: str,
        tenant_id: str,
        payload: dict[str, Any],
    ) -> WorkflowContext:
        ctx = WorkflowContext(
            workflow_id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            correlation_id=correlation_id,
            tenant_id=tenant_id,
            payload=payload,
        )

        logger.info(
            "workflow.started",
            workflow_id=ctx.workflow_id,
            transaction_id=transaction_id,
        )

        for step in self._steps:
            logger.info("step.executing", step=step.name, workflow_id=ctx.workflow_id)
            result = await step.execute(ctx)
            ctx.add_result(result)
            logger.info(
                "step.result",
                step=step.name,
                status=result.status,
                workflow_id=ctx.workflow_id,
            )

            if result.status == StepStatus.FAILED:
                logger.warning(
                    "workflow.step_failed",
                    step=step.name,
                    error=result.error,
                    workflow_id=ctx.workflow_id,
                )
                # Rollback completed steps in reverse
                for completed_step in reversed(self._steps[: self._steps.index(step)]):
                    try:
                        await completed_step.rollback(ctx)
                    except Exception as exc:
                        logger.error(
                            "step.rollback_error", step=completed_step.name, error=str(exc)
                        )
                break

        final_status = "failed" if ctx.has_failed() else "completed"
        logger.info(
            "workflow.finished",
            workflow_id=ctx.workflow_id,
            transaction_id=transaction_id,
            status=final_status,
        )
        return ctx
