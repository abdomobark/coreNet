from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class MetricRead(BaseModel):
    id: int
    device_id: int
    metric_type: str
    metric_value: Dict[str, Any]
    severity: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class AlertRead(BaseModel):
    id: int
    device_id: Optional[int] = None
    alert_type: str
    severity: str
    message: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ResolveAlertRequest(BaseModel):
    message: Optional[str] = None
