from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db
from backend.app.schemas.auth import LoginRequest, TokenResponse
from backend.app.schemas.user import UserRead
from backend.app.security.authz import get_current_user
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    token = await AuthService(db).authenticate(payload.username_or_email, payload.password)
    return TokenResponse(access_token=token)

@router.get("/me", response_model=UserRead)
async def me(user = Depends(get_current_user)):
    return user
