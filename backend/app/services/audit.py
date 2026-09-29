from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.logging import AuditLog

async def log_audit(
    db: AsyncSession,
    *,
    user_id: Optional[int],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    device_id: Optional[int] = None,
    source_ip: Optional[str] = None,
    status_text: Optional[str] = None,
    details: Optional[str] = None,
) -> None:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        device_id=device_id,
        source_ip=source_ip,
        status=status_text,
        details=details,
    )
    db.add(entry)
    await db.flush()
