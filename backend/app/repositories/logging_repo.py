from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.logging import SystemLog, AuditLog

class LoggingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_system_logs(self, *, level: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[SystemLog]:
        stmt = select(SystemLog).order_by(SystemLog.id.desc())
        if level is not None:
            stmt = stmt.where(SystemLog.level == level)
        stmt = stmt.offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def list_audit_logs(self, *, user_id: Optional[int] = None, action: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.id.desc())
        if user_id is not None:
            stmt = stmt.where(AuditLog.user_id == user_id)
        if action is not None:
            stmt = stmt.where(AuditLog.action == action)
        stmt = stmt.offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
