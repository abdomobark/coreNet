from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db
from backend.app.security.rbac import require_permissions, get_current_user
from backend.app.schemas.user import UserRead, UserUpdate, UserPasswordChange, UserAssignRoles, RoleRead
from backend.app.repositories.user_repo import UserRepository
from backend.app.repositories.rbac_repo import RBACRepository
from backend.app.services.audit import log_audit

router = APIRouter(prefix="/users-admin", tags=["users-admin"])

@router.put("/{user_id}", response_model=UserRead, dependencies=[Depends(require_permissions("users:manage"))])
async def update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db), actor=Depends(get_current_user)):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated = await repo.update(user, payload.model_dump(exclude_unset=True))
    await log_audit(db, user_id=actor.id, action="user.update", resource_type="user", resource_id=user_id, details=payload.model_dump_json())
    await db.commit()
    return updated

@router.post("/{user_id}/password", response_model=UserRead, dependencies=[Depends(require_permissions("users:manage"))])
async def change_password(user_id: int, payload: UserPasswordChange, db: AsyncSession = Depends(get_db), actor=Depends(get_current_user)):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await repo.set_password(user, payload.new_password)
    await log_audit(db, user_id=actor.id, action="user.password.change", resource_type="user", resource_id=user_id)
    await db.commit()
    return user

@router.get("/{user_id}/roles", response_model=List[RoleRead], dependencies=[Depends(require_permissions("users:view"))])
async def list_user_roles(user_id: int, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.roles

@router.post("/{user_id}/roles", response_model=List[RoleRead], dependencies=[Depends(require_permissions("users:manage"))])
async def assign_roles(user_id: int, payload: UserAssignRoles, db: AsyncSession = Depends(get_db), actor=Depends(get_current_user)):
    urepo = UserRepository(db)
    rrepo = RBACRepository(db)
    user = await urepo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # assign roles
    for rid in payload.role_ids:
        role = await rrepo.get_role_by_id(rid)
        if not role:
            raise HTTPException(status_code=404, detail=f"Role {rid} not found")
        await urepo.add_role(user, role)
    await log_audit(db, user_id=actor.id, action="user.roles.assign", resource_type="user", resource_id=user_id, details=str(payload.role_ids))
    await db.commit()
    return user.roles

@router.delete("/{user_id}/roles/{role_id}", response_model=List[RoleRead], dependencies=[Depends(require_permissions("users:manage"))])
async def remove_role(user_id: int, role_id: int, db: AsyncSession = Depends(get_db), actor=Depends(get_current_user)):
    urepo = UserRepository(db)
    rrepo = RBACRepository(db)
    user = await urepo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role = await rrepo.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    await urepo.remove_role(user, role)
    await log_audit(db, user_id=actor.id, action="user.roles.remove", resource_type="user", resource_id=user_id, details=str(role_id))
    await db.commit()
    return user.roles
