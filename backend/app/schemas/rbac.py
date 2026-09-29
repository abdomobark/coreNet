from typing import Optional, List
from pydantic import BaseModel, Field

class PermissionRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class PermissionCreate(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class RoleDetailRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[PermissionRead] = Field(default_factory=list)

    class Config:
        from_attributes = True
