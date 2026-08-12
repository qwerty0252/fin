from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db.database import get_db
from app.models.transaction import TransactionStatus
from app.schemas.transaction_schemas import (
    CreateTransactionRequest,
    TransactionResponse,
    TransactionStatusUpdateRequest,
)
from app.services.transaction_service import TransactionService

router = APIRouter()


def _serialize(txn) -> TransactionResponse:
    return TransactionResponse(
        id=txn.id,
        reference=txn.reference,
        correlation_id=txn.correlation_id,
        tenant_id=txn.tenant_id,
        transaction_type=txn.transaction_type,
        status=txn.status,
        amount=txn.amount,
        currency=txn.currency,
        sender_account=txn.sender_account,
        receiver_account=txn.receiver_account,
        description=txn.description,
        channel=txn.channel,
        created_at=txn.created_at.isoformat(),
        updated_at=txn.updated_at.isoformat(),
    )


@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    body: CreateTransactionRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TransactionResponse:
    svc = TransactionService(db, settings)
    txn = await svc.create_transaction(body.model_dump())
    return _serialize(txn)


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TransactionResponse:
    svc = TransactionService(db, settings)
    txn = await svc.get_transaction(transaction_id)
    if not txn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return _serialize(txn)


@router.patch("/transactions/{transaction_id}/status", response_model=TransactionResponse)
async def update_transaction_status(
    transaction_id: str,
    body: TransactionStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TransactionResponse:
    svc = TransactionService(db, settings)
    txn = await svc.get_transaction(transaction_id)
    if not txn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    try:
        new_status = TransactionStatus(body.status)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {body.status}"
        ) from exc
    txn = await svc.update_status(txn, new_status, body.failure_reason, body.external_ref)
    return _serialize(txn)
