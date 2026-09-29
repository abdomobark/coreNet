from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class ConfigurationVersionRead(BaseModel):
    id: int
    version: int
    config_text: str
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ConfigurationRead(BaseModel):
    id: int
    device_id: int
    current_version_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CreateVersionRequest(BaseModel):
    config_text: str
    created_by: Optional[int] = None

class SetCurrentRequest(BaseModel):
    version_id: int
