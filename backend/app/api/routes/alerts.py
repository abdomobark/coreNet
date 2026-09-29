from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db
from backend.app.security.rbac import require_permissions
from backend.app.schemas.monitoring import AlertRead, ResolveAlertRequest
from backend.app.repositories.monitoring_repo import MonitoringRepository

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("", response_model=List[AlertRead], dependencies=[Depends(require_permissions("alerts:view"))])
async def list_alerts(
    db: AsyncSession = Depends(get_db),
    status_: Optional[str] = Query(None, alias="status"),
    device_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    alerts = await MonitoringRepository(db).list_alerts(status=status_, device_id=device_id, skip=skip, limit=limit)
    return [AlertRead.model_validate(a) for a in alerts]

@router.post("/{alert_id}/resolve", response_model=AlertRead, dependencies=[Depends(require_permissions("alerts:manage"))])
async def resolve_alert(alert_id: int, _: ResolveAlertRequest, db: AsyncSession = Depends(get_db)):
    repo = MonitoringRepository(db)
    alert = await repo.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert = await repo.resolve_alert(alert)
    await db.commit()
    return AlertRead.model_validate(alert)
