class AppError(Exception):
    """Base class for all domain-level errors."""

    status_code: int = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class EmailAlreadyRegisteredError(AppError):
    status_code = 409


class InvalidCredentialsError(AppError):
    status_code = 401


class UserNotFoundError(AppError):
    status_code = 404


class InvalidTokenPayloadError(AppError):
    status_code = 401


class GoogleTokenVerificationError(AppError):
    status_code = 401
