from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class OperationCreate(BaseModel):
    device_id: Optional[int] = None
    operation_type: str
    command: Optional[str] = None

class OperationRead(BaseModel):
    id: int
    user_id: Optional[int] = None
    device_id: Optional[int] = None
    operation_type: str
    command: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
