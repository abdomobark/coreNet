from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class NotificationCreate(BaseModel):
    user_id: Optional[int] = None
    channel: str  # email, slack, webhook
    subject: Optional[str] = None
    body: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class NotificationRead(BaseModel):
    id: int
    user_id: Optional[int] = None
    channel: str
    subject: Optional[str] = None
    body: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    status: str
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
