from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    GoogleAuthRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(payload: UserRegisterRequest, service: AuthService = Depends(get_auth_service)):
    return await service.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest, service: AuthService = Depends(get_auth_service)):
    return await service.login(payload)


@router.post("/google", response_model=TokenResponse)
async def google_login(payload: GoogleAuthRequest, service: AuthService = Depends(get_auth_service)):
    return await service.login_with_google(payload.id_token)


@router.post("/refresh")
async def refresh(payload: RefreshTokenRequest, service: AuthService = Depends(get_auth_service)):
    new_access_token = await service.refresh_access_token(payload.refresh_token)
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
