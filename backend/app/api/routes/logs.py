from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db
from backend.app.security.rbac import require_permissions
from backend.app.schemas.logging import SystemLogRead, AuditLogRead
from backend.app.repositories.logging_repo import LoggingRepository

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("/system", response_model=List[SystemLogRead], dependencies=[Depends(require_permissions("logs:view"))])
async def list_system_logs(
    db: AsyncSession = Depends(get_db),
    level: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    logs = await LoggingRepository(db).list_system_logs(level=level, skip=skip, limit=limit)
    return [SystemLogRead.model_validate(l) for l in logs]

@router.get("/audit", response_model=List[AuditLogRead], dependencies=[Depends(require_permissions("audit:view"))])
async def list_audit_logs(
    db: AsyncSession = Depends(get_db),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    logs = await LoggingRepository(db).list_audit_logs(user_id=user_id, action=action, skip=skip, limit=limit)
    return [AuditLogRead.model_validate(l) for l in logs]
