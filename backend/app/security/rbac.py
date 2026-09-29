from typing import Callable, Optional, Set

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, join

from backend.app.api.deps import get_db
from backend.app.security.jwt import decode_token
from backend.app.models.user import User
from backend.app.models.rbac import Permission, user_roles, role_permissions

async def get_current_user(authorization: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = await db.get(User, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    return user

def require_permissions(*required: str) -> Callable:
    async def _checker(current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> User:
        # Build a join: user_roles -> role_permissions -> permissions
        j = user_roles.join(role_permissions, user_roles.c.role_id == role_permissions.c.role_id) \
                      .join(Permission, role_permissions.c.permission_id == Permission.id)
        stmt = select(Permission.name).select_from(j).where(user_roles.c.user_id == current.id)
        res = await db.execute(stmt)
        user_perm_names: Set[str] = set(res.scalars().all())
        missing = [p for p in required if p not in user_perm_names]
        if missing:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing permissions: {', '.join(missing)}")
        return current
    return _checker
