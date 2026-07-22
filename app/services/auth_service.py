import uuid

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.utils.exceptions import (
    EmailAlreadyRegisteredError,
    GoogleTokenVerificationError,
    InvalidCredentialsError,
    InvalidTokenPayloadError,
    UserNotFoundError,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def _issue_tokens(self, user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
            user=UserResponse.model_validate(user),
        )

    async def register(self, payload: UserRegisterRequest) -> TokenResponse:
        existing = await self.user_repo.get_by_email(payload.email)
        if existing:
            raise EmailAlreadyRegisteredError(f"{payload.email} is already registered")

        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            auth_provider="local",
            is_active=True,
            is_verified=False,
        )
        user = await self.user_repo.create(user)
        logger.info("New user registered: %s", user.email)
        return self._issue_tokens(user)

    async def login(self, payload: UserLoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(payload.email)
        if not user or not user.hashed_password:
            raise InvalidCredentialsError("Incorrect email or password")

        if not verify_password(payload.password, user.hashed_password):
            raise InvalidCredentialsError("Incorrect email or password")

        logger.info("User logged in: %s", user.email)
        return self._issue_tokens(user)

    async def login_with_google(self, id_token_str: str) -> TokenResponse:
        try:
            idinfo = google_id_token.verify_oauth2_token(
                id_token_str, google_requests.Request(), settings.GOOGLE_CLIENT_ID
            )
        except ValueError as exc:
            raise GoogleTokenVerificationError("Invalid Google ID token") from exc

        google_id = idinfo["sub"]
        email = idinfo["email"]
        full_name = idinfo.get("name", email.split("@")[0])

        user = await self.user_repo.get_by_google_id(google_id)
        if not user:
            # Link by email if the account already exists locally, else create new
            user = await self.user_repo.get_by_email(email)
            if not user:
                user = User(
                    email=email,
                    full_name=full_name,
                    auth_provider="google",
                    google_id=google_id,
                    is_verified=True,
                )
                user = await self.user_repo.create(user)
                logger.info("New Google user created: %s", email)

        return self._issue_tokens(user)

    async def refresh_access_token(self, refresh_token: str) -> str:
        try:
            user_id = decode_token(refresh_token, expected_type="refresh")
        except Exception as exc:
            raise InvalidTokenPayloadError("Invalid or expired refresh token") from exc

        user = await self.user_repo.get_by_id(uuid.UUID(user_id))
        if not user:
            raise UserNotFoundError("User no longer exists")

        return create_access_token(str(user.id))
