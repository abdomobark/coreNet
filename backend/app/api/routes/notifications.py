from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db
from backend.app.security.rbac import require_permissions
from backend.app.schemas.notification import NotificationCreate, NotificationRead
from backend.app.repositories.notification_repo import NotificationRepository
from backend.app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("", response_model=List[NotificationRead], dependencies=[Depends(require_permissions("notifications:view"))])
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    status_: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    return await NotificationRepository(db).list(status=status_, skip=skip, limit=limit)

@router.post("", response_model=NotificationRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions("notifications:manage"))])
async def create_notification(payload: NotificationCreate, db: AsyncSession = Depends(get_db)):
    n = await NotificationRepository(db).create(payload.model_dump())
    await db.commit()
    return n

@router.post("/{notification_id}/send", response_model=NotificationRead, dependencies=[Depends(require_permissions("notifications:manage"))])
async def send_notification(notification_id: int, db: AsyncSession = Depends(get_db)):
    repo = NotificationRepository(db)
    n = await repo.get(notification_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    sent = await NotificationService(repo).send(n)
    await db.commit()
    return sent
