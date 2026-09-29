from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.rbac import Role, Permission
from backend.app.models.user import User

class RBACRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Permissions
    async def list_permissions(self) -> List[Permission]:
        res = await self.db.execute(select(Permission).order_by(Permission.name.asc()))
        return list(res.scalars().all())

    async def get_permission_by_id(self, permission_id: int) -> Optional[Permission]:
        return await self.db.get(Permission, permission_id)

    async def get_or_create_permission(self, name: str, description: str | None = None) -> Permission:
        res = await self.db.execute(select(Permission).where(Permission.name == name))
        perm = res.scalars().first()
        if perm:
            return perm
        perm = Permission(name=name, description=description)
        self.db.add(perm)
        await self.db.flush()
        return perm

    async def delete_permission(self, permission: Permission) -> None:
        await self.db.delete(permission)

    # Roles
    async def list_roles(self) -> List[Role]:
        res = await self.db.execute(select(Role).order_by(Role.name.asc()))
        return list(res.scalars().all())

    async def get_role_by_id(self, role_id: int) -> Optional[Role]:
        return await self.db.get(Role, role_id)

    async def get_or_create_role(self, name: str, description: str | None = None) -> Role:
        res = await self.db.execute(select(Role).where(Role.name == name))
        role = res.scalars().first()
        if role:
            return role
        role = Role(name=name, description=description)
        self.db.add(role)
        await self.db.flush()
        return role

    async def delete_role(self, role: Role) -> None:
        await self.db.delete(role)

    async def ensure_role_permission(self, role: Role, permission: Permission) -> None:
        # Load the collection async-safely: on a freshly-inserted Role the
        # lazy="selectin" loader does not fire, so a plain access would raise
        # MissingGreenlet inside the async session.
        perms = await role.awaitable_attrs.permissions
        if permission not in perms:
            perms.append(permission)
            await self.db.flush()

    async def set_role_permissions(self, role: Role, permissions: List[Permission]) -> Role:
        # Ensure the existing collection is loaded before replacing it, otherwise
        # the assignment triggers a synchronous lazy-load to compute the diff.
        await role.awaitable_attrs.permissions
        role.permissions = permissions
        await self.db.flush()
        return role

    # Users <-> Roles
    async def ensure_user_role(self, user: User, role: Role) -> None:
        users = await role.awaitable_attrs.users
        if user not in users:
            users.append(user)
            await self.db.flush()

    async def remove_user_role(self, user: User, role: Role) -> None:
        users = await role.awaitable_attrs.users
        if user in users:
            users.remove(user)
            await self.db.flush()
