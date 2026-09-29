from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db
from backend.app.security.rbac import require_permissions
from backend.app.schemas.user import UserRead
from backend.app.repositories.user_repo import UserRepository

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[UserRead], dependencies=[Depends(require_permissions("users:view"))])
async def list_users(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    users = await UserRepository(db).list_users(skip=skip, limit=limit)
    return users
