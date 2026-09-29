from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.user_repo import UserRepository
from backend.app.security.passwords import verify_password
from backend.app.security.jwt import create_token
from backend.app.core.config import settings

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)

    async def authenticate(self, username_or_email: str, password: str) -> str:
        user = await self.users.get_by_username_or_email(username_or_email)
        if not user or not verify_password(password, user.password_hash):
            # increment failed attempts
            if user:
                user.failed_login_attempts += 1
            await self.db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
        # reset counters; set last_login
        user.failed_login_attempts = 0
        user.last_login = datetime.now(timezone.utc)
        await self.db.commit()
        # issue access token
        return create_token(user.id, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
