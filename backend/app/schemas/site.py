from typing import Optional, List
from pydantic import BaseModel

class SiteCreate(BaseModel):
    name: str
    code: str
    location: Optional[str] = None
    description: Optional[str] = None

class SiteUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

class SiteRead(BaseModel):
    id: int
    name: str
    code: str
    location: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True
