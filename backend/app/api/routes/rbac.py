from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db
from backend.app.security.rbac import require_permissions, get_current_user
from backend.app.schemas.rbac import PermissionRead, PermissionCreate, RoleCreate, RoleUpdate, RoleDetailRead
from backend.app.schemas.user import RoleRead
from backend.app.repositories.rbac_repo import RBACRepository
from backend.app.services.audit import log_audit

router = APIRouter(prefix="/rbac", tags=["rbac"])

# Permissions
@router.get("/permissions", response_model=List[PermissionRead], dependencies=[Depends(require_permissions("users:view"))])
async def list_permissions(db: AsyncSession = Depends(get_db)):
    return await RBACRepository(db).list_permissions()

@router.post("/permissions", response_model=PermissionRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions("settings:manage"))])
async def create_permission(payload: PermissionCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    repo = RBACRepository(db)
    perm = await repo.get_or_create_permission(payload.name, payload.description)
    await log_audit(db, user_id=user.id, action="permission.create", resource_type="permission", resource_id=perm.id, details=payload.model_dump_json())
    await db.commit()
    return perm

@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permissions("settings:manage"))])
async def delete_permission(permission_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    repo = RBACRepository(db)
    perm = await repo.get_permission_by_id(permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    await repo.delete_permission(perm)
    await log_audit(db, user_id=user.id, action="permission.delete", resource_type="permission", resource_id=permission_id)
    await db.commit()
    return None

# Roles
@router.get("/roles", response_model=List[RoleRead], dependencies=[Depends(require_permissions("users:view"))])
async def list_roles(db: AsyncSession = Depends(get_db)):
    roles = await RBACRepository(db).list_roles()
    return roles

@router.post("/roles", response_model=RoleDetailRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions("settings:manage"))])
async def create_role(payload: RoleCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    repo = RBACRepository(db)
    role = await repo.get_or_create_role(payload.name, payload.description)
    await log_audit(db, user_id=user.id, action="role.create", resource_type="role", resource_id=role.id, details=payload.model_dump_json())
    await db.commit()
    # A freshly-inserted Role has no selectin-loaded `permissions` collection, so
    # serializing RoleDetailRead would trigger a lazy load and raise MissingGreenlet.
    # Load it async-safely before returning.
    await role.awaitable_attrs.permissions
    return role

@router.get("/roles/{role_id}", response_model=RoleDetailRead, dependencies=[Depends(require_permissions("users:view"))])
async def get_role(role_id: int, db: AsyncSession = Depends(get_db)):
    role = await RBACRepository(db).get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/roles/{role_id}", response_model=RoleDetailRead, dependencies=[Depends(require_permissions("settings:manage"))])
async def update_role(role_id: int, payload: RoleUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    repo = RBACRepository(db)
    role = await repo.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        role.name = data["name"]
    if "description" in data:
        role.description = data["description"]
    await log_audit(db, user_id=user.id, action="role.update", resource_type="role", resource_id=role.id, details=payload.model_dump_json())
    await db.commit()
    return role

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permissions("settings:manage"))])
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    repo = RBACRepository(db)
    role = await repo.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    await repo.delete_role(role)
    await log_audit(db, user_id=user.id, action="role.delete", resource_type="role", resource_id=role_id)
    await db.commit()
    return None

@router.put("/roles/{role_id}/permissions", response_model=RoleDetailRead, dependencies=[Depends(require_permissions("settings:manage"))])
async def set_role_permissions(role_id: int, permission_ids: List[int], db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    repo = RBACRepository(db)
    role = await repo.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    perms = []
    for pid in permission_ids:
        p = await repo.get_permission_by_id(pid)
        if not p:
            raise HTTPException(status_code=404, detail=f"Permission {pid} not found")
        perms.append(p)
    await repo.set_role_permissions(role, perms)
    await log_audit(db, user_id=user.id, action="role.permissions.set", resource_type="role", resource_id=role.id, details=str(permission_ids))
    await db.commit()
    return role
