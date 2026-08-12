import uuid
from typing import Any

import httpx

from app.config import Settings
from app.workflows.base import StepResult, StepStatus, WorkflowContext, WorkflowStep
from shared.utils.logging import get_logger

logger = get_logger(__name__)


class ValidationStep(WorkflowStep):
    name = "validation"

    async def execute(self, ctx: WorkflowContext) -> StepResult:
        payload = ctx.payload
        errors = []
        if not payload.get("amount") or float(payload["amount"]) <= 0:
            errors.append("Invalid amount")
        if not payload.get("sender_account"):
            errors.append("Missing sender_account")
        if not payload.get("receiver_account"):
            errors.append("Missing receiver_account")

        if errors:
            return StepResult(
                step_name=self.name,
                status=StepStatus.FAILED,
                error=f"Validation failed: {', '.join(errors)}",
            )
        return StepResult(step_name=self.name, status=StepStatus.COMPLETED, output={"valid": True})

    async def rollback(self, ctx: WorkflowContext) -> None:
        pass


class FraudCheckStep(WorkflowStep):
    name = "fraud_check"

    async def execute(self, ctx: WorkflowContext) -> StepResult:
        # Phase 1: mock fraud check — flag high-value transactions
        amount = float(ctx.payload.get("amount", 0))
        if amount > 10_000_000:
            return StepResult(
                step_name=self.name,
                status=StepStatus.FAILED,
                error="Transaction flagged: exceeds single-transaction limit",
            )
        return StepResult(
            step_name=self.name,
            status=StepStatus.COMPLETED,
            output={"fraud_score": 0.02, "approved": True},
        )

    async def rollback(self, ctx: WorkflowContext) -> None:
        pass


class RoutingStep(WorkflowStep):
    name = "routing"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def execute(self, ctx: WorkflowContext) -> StepResult:
        receiver_bank = ctx.payload.get("receiver_bank_code", "000")
        # Phase 1: always route to mock switch
        selected_connector = "mock_payment_switch"
        return StepResult(
            step_name=self.name,
            status=StepStatus.COMPLETED,
            output={"connector": selected_connector, "receiver_bank": receiver_bank},
        )

    async def rollback(self, ctx: WorkflowContext) -> None:
        pass


class PaymentSubmissionStep(WorkflowStep):
    name = "payment_submission"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def execute(self, ctx: WorkflowContext) -> StepResult:
        routing_output = {}
        for r in ctx.step_results:
            if r.step_name == "routing" and r.status == StepStatus.COMPLETED:
                routing_output = r.output

        connector = routing_output.get("connector", "mock_payment_switch")
        try:
            async with httpx.AsyncClient(timeout=self._settings.step_timeout) as client:
                response = await client.post(
                    f"{self._settings.connector_service_url}/api/v1/connectors/{connector}/submit",
                    json={
                        "transaction_id": ctx.transaction_id,
                        "correlation_id": ctx.correlation_id,
                        **ctx.payload,
                    },
                )
                if response.status_code >= 400:
                    return StepResult(
                        step_name=self.name,
                        status=StepStatus.FAILED,
                        error=f"Connector rejected: {response.text}",
                    )
                return StepResult(
                    step_name=self.name,
                    status=StepStatus.COMPLETED,
                    output=response.json(),
                )
        except Exception as exc:
            return StepResult(
                step_name=self.name, status=StepStatus.FAILED, error=str(exc)
            )

    async def rollback(self, ctx: WorkflowContext) -> None:
        logger.warning("payment_submission.rollback_not_implemented", txn_id=ctx.transaction_id)


class NotificationStep(WorkflowStep):
    name = "notification"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def execute(self, ctx: WorkflowContext) -> StepResult:
        final_status = "completed" if not ctx.has_failed() else "failed"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"{self._settings.notification_service_url}/api/v1/notify",
                    json={
                        "transaction_id": ctx.transaction_id,
                        "correlation_id": ctx.correlation_id,
                        "tenant_id": ctx.tenant_id,
                        "status": final_status,
                        "channel": "webhook",
                    },
                )
        except Exception as exc:
            logger.warning("notification_step.failed", error=str(exc))
        return StepResult(
            step_name=self.name,
            status=StepStatus.COMPLETED,
            output={"notified": True},
        )

    async def rollback(self, ctx: WorkflowContext) -> None:
        pass
