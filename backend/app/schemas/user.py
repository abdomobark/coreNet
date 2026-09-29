from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class RoleRead(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    last_login: Optional[datetime] = None
    roles: List[RoleRead] = Field(default_factory=list)
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_active: bool = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserPasswordChange(BaseModel):
    new_password: str

class UserAssignRoles(BaseModel):
    role_ids: List[int]
