from typing import Optional, List

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.models.rbac import Role
from backend.app.security.passwords import hash_password

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await self.db.get(User, user_id)

    async def get_by_username_or_email(self, value: str) -> Optional[User]:
        stmt = select(User).where(or_(User.username == value, User.email == value))
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def create(self, username: str, email: str, password: str, is_active: bool = True) -> User:
        user = User(username=username, email=email, password_hash=hash_password(password), is_active=is_active)
        self.db.add(user)
        await self.db.flush()
        return user

    async def list_users(self, skip: int = 0, limit: int = 50) -> List[User]:
        stmt = select(User).offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def add_role(self, user: User, role: Role) -> None:
        # Load async-safely: a freshly-inserted User has no selectin-loaded
        # roles collection, so a plain access would raise MissingGreenlet.
        roles = await user.awaitable_attrs.roles
        if role not in roles:
            roles.append(role)
            await self.db.flush()

    async def remove_role(self, user: User, role: Role) -> None:
        roles = await user.awaitable_attrs.roles
        if role in roles:
            roles.remove(role)
            await self.db.flush()

    async def set_password(self, user: User, new_password: str) -> None:
        user.password_hash = hash_password(new_password)
        await self.db.flush()

    async def update(self, user: User, data: dict) -> User:
        for k, v in data.items():
            if v is not None and hasattr(user, k):
                setattr(user, k, v)
        await self.db.flush()
        return user
