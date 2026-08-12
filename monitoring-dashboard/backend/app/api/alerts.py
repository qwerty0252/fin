"""Add alerts endpoint to API"""

from fastapi import APIRouter, Depends, HTTPException
from app.schemas import AlertResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Alert
from app.utils import get_session

router = APIRouter(prefix="/api", tags=["alerts"])


@router.get("/alerts", response_model=list[AlertResponse])
async def get_alerts(db: AsyncSession = Depends(get_session)):
    """Get all alerts"""
    result = await db.execute(select(Alert).order_by(Alert.created_at.desc()))
    alerts = result.scalars().all()
    return [AlertResponse.model_validate(a) for a in alerts]


@router.get("/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_session)):
    """Get a specific alert"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse.model_validate(alert)


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, db: AsyncSession = Depends(get_session)):
    """Resolve an alert"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = "RESOLVED"
    await db.commit()
    return {"status": "resolved", "alert_id": alert_id}
