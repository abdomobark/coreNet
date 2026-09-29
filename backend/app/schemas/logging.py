from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class SystemLogRead(BaseModel):
    id: int
    level: str
    message: str
    logger: Optional[str] = None
    user_id: Optional[int] = None
    device_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogRead(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    device_id: Optional[int] = None
    source_ip: Optional[str] = None
    status: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
