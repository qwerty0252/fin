from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.workflows.base import StepStatus
from app.workflows.payment_workflow import PaymentWorkflow

router = APIRouter()


class WorkflowRequest(BaseModel):
    transaction_id: str
    correlation_id: str
    tenant_id: str
    payload: dict[str, Any]


class WorkflowResponse(BaseModel):
    workflow_id: str
    transaction_id: str
    status: str
    steps: list[dict[str, Any]]
    error: str | None = None


@router.post("/workflows/payment", response_model=WorkflowResponse)
async def execute_payment_workflow(
    body: WorkflowRequest,
    settings: Settings = Depends(get_settings),
) -> WorkflowResponse:
    workflow = PaymentWorkflow(settings)
    ctx = await workflow.execute(
        transaction_id=body.transaction_id,
        correlation_id=body.correlation_id,
        tenant_id=body.tenant_id,
        payload=body.payload,
    )
    final_status = "failed" if ctx.has_failed() else "completed"
    failed_step = next((r for r in ctx.step_results if r.status == StepStatus.FAILED), None)
    return WorkflowResponse(
        workflow_id=ctx.workflow_id,
        transaction_id=body.transaction_id,
        status=final_status,
        steps=[r.model_dump() for r in ctx.step_results],
        error=failed_step.error if failed_step else None,
    )
