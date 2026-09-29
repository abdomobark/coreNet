from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.logging import Notification

class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, *, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Notification]:
        stmt = select(Notification).order_by(Notification.id.desc())
        if status:
            stmt = stmt.where(Notification.status == status)
        stmt = stmt.offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get(self, notification_id: int) -> Optional[Notification]:
        return await self.db.get(Notification, notification_id)

    async def create(self, data: dict) -> Notification:
        n = Notification(**data)
        self.db.add(n)
        await self.db.flush()
        return n

    async def list_pending(self, limit: int = 50) -> List[Notification]:
        res = await self.db.execute(
            select(Notification).where(Notification.status == "pending").order_by(Notification.id.asc()).limit(limit)
        )
        return list(res.scalars().all())

    async def mark_sent(self, notification: Notification) -> Notification:
        notification.status = "sent"
        notification.sent_at = datetime.now(timezone.utc)
        await self.db.flush()
        return notification

    async def mark_error(self, notification: Notification, error: str | None = None) -> Notification:
        notification.status = "error"
        # Assuming there is a field 'error' or meta to store error; using meta if present
        try:
            if hasattr(notification, "meta") and isinstance(notification.meta, dict):  # type: ignore[attr-defined]
                notification.meta["error"] = error  # type: ignore[index]
        except Exception:
            pass
        await self.db.flush()
        return notification
