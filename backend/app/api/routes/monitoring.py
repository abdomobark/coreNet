from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db
from backend.app.security.rbac import require_permissions, get_current_user
from backend.app.security.api_keys import require_agent_api_key
from backend.app.schemas.monitoring import MetricRead
from backend.app.repositories.monitoring_repo import MonitoringRepository
from backend.app.services.audit import log_audit

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/metrics", response_model=List[MetricRead], dependencies=[Depends(require_permissions("monitoring:view"))])
async def list_metrics(
    db: AsyncSession = Depends(get_db),
    device_id: Optional[int] = Query(None),
    metric_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    return await MonitoringRepository(db).list_metrics(device_id=device_id, metric_type=metric_type, skip=skip, limit=limit)

@router.post(
    "/metrics",
    response_model=MetricRead,
    dependencies=[Depends(require_permissions("monitoring:ingest")), Depends(require_agent_api_key)],
)
async def ingest_metric(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    # expected payload: { device_id:int, metric_type:str, metric_value:dict, severity:Optional[str], timestamp:Optional[str ISO] }
    device_id = int(payload["device_id"])
    metric_type = str(payload["metric_type"])
    metric_value = payload.get("metric_value") or {}
    severity = payload.get("severity")
    ts = payload.get("timestamp")
    timestamp = datetime.fromisoformat(ts) if isinstance(ts, str) else None
    repo = MonitoringRepository(db)
    mm = await repo.ingest_metric(device_id=device_id, metric_type=metric_type, metric_value=metric_value, severity=severity, timestamp=timestamp)
    await log_audit(db, user_id=user.id if user else None, action="monitoring.metrics.ingest", resource_type="device", resource_id=device_id)
    await db.commit()
    return mm
