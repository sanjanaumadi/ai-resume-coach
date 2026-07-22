import uuid

import pytest

from app.core.security import hash_password
from app.models.user import User
from app.schemas.auth import UserLoginRequest, UserRegisterRequest
from app.services.auth_service import AuthService
from app.utils.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError


class FakeUserRepository:
    """In-memory stand-in for UserRepository — no DB needed for these tests."""

    def __init__(self):
        self._users: dict[str, User] = {}

    async def get_by_email(self, email: str) -> User | None:
        return self._users.get(email)

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return next((u for u in self._users.values() if u.id == user_id), None)

    async def get_by_google_id(self, google_id: str) -> User | None:
        return next((u for u in self._users.values() if u.google_id == google_id), None)

    async def create(self, user: User) -> User:
        user.id = user.id or uuid.uuid4()
        self._users[user.email] = user
        return user


@pytest.fixture
def auth_service():
    return AuthService(FakeUserRepository())


@pytest.mark.asyncio
async def test_register_creates_user_and_returns_tokens(auth_service):
    payload = UserRegisterRequest(email="sanj@example.com", full_name="Sanj", password="strongpass123")
    result = await auth_service.register(payload)

    assert result.user.email == "sanj@example.com"
    assert result.access_token
    assert result.refresh_token


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email(auth_service):
    payload = UserRegisterRequest(email="sanj@example.com", full_name="Sanj", password="strongpass123")
    await auth_service.register(payload)

    with pytest.raises(EmailAlreadyRegisteredError):
        await auth_service.register(payload)


@pytest.mark.asyncio
async def test_login_succeeds_with_correct_password(auth_service):
    await auth_service.register(
        UserRegisterRequest(email="sanj@example.com", full_name="Sanj", password="strongpass123")
    )
    result = await auth_service.login(
        UserLoginRequest(email="sanj@example.com", password="strongpass123")
    )
    assert result.user.email == "sanj@example.com"


@pytest.mark.asyncio
async def test_login_fails_with_wrong_password(auth_service):
    await auth_service.register(
        UserRegisterRequest(email="sanj@example.com", full_name="Sanj", password="strongpass123")
    )
    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(UserLoginRequest(email="sanj@example.com", password="wrongpass"))


@pytest.mark.asyncio
async def test_login_fails_for_unknown_email(auth_service):
    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(UserLoginRequest(email="nobody@example.com", password="whatever123"))


def test_password_hash_is_not_plaintext():
    hashed = hash_password("mypassword")
    assert hashed != "mypassword"
    assert hashed.startswith("$2b$")
