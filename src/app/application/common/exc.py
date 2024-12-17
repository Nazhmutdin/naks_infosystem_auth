from uuid import UUID

from app.application.common import ExceptionCodes


class AccessForbidden(Exception): 
    def __init__(self, code: ExceptionCodes = ExceptionCodes.ACCESS_FORBIDDEN) -> None:
        self.code = code


class UserNotFound(Exception):
    def __init__(
        self, 
        ident: UUID | str,
        code: ExceptionCodes = ExceptionCodes.USER_NOT_FOUND
    ) -> None:
        self.ident = ident
        self.code = code


class InvalidPassword(Exception):
    def __init__(self, code: ExceptionCodes = ExceptionCodes.INVALID_PASSWORD) -> None:
        self.code = code


class InvalidRefreshToken(Exception):
    def __init__(self, code: ExceptionCodes = ExceptionCodes.INVALID_REFRESH_TOKEN) -> None:
        self.code = code


class InvalidAccessToken(Exception):
    def __init__(self, code: ExceptionCodes = ExceptionCodes.INVALID_ACCESS_TOKEN) -> None:
        self.code = code


class RefreshTokenCookieNotFound(Exception):
    def __init__(self, code: ExceptionCodes = ExceptionCodes.REFRESH_TOKEN_COOKIE_NOT_FOUND) -> None:
        self.code = code


class AccessTokenCookieNotFound(Exception):
    def __init__(self, code: ExceptionCodes = ExceptionCodes.ACCESS_TOKEN_COOKIE_NOT_FOUND) -> None:
        self.code = code


class RefreshTokenNotFound(Exception):
    def __init__(
        self, 
        ident: UUID,
        code: ExceptionCodes = ExceptionCodes.REFRESH_TOKEN_NOT_FOUND
    ) -> None:
        self.ident = ident
        self.code = code


class RefreshTokenRevoked(Exception): 
    def __init__(self, code: ExceptionCodes = ExceptionCodes.REFRESH_TOKEN_REVOKED) -> None:
        self.code = code


class RefreshTokenExpired(Exception): 
    def __init__(self, code: ExceptionCodes = ExceptionCodes.REFRESH_TOKEN_EXPIRED) -> None:
        self.code = code


class AccessTokenExpired(Exception): 
    def __init__(self, code: ExceptionCodes = ExceptionCodes.ACCESS_TOKEN_EXPIRED) -> None:
        self.code = code


class PermissionDataNotFound(Exception): 
    def __init__(self, user_ident: UUID, code: ExceptionCodes = ExceptionCodes.PERMISSION_DATA_NOT_FOUND):
        self.user_ident = user_ident
        self.code = code


class OriginalMethodNotFound(Exception): 
    def __init__(self, code: ExceptionCodes = ExceptionCodes.ORIGINAL_METHOD_NOT_FOUND) -> None:
        self.code = code


class OriginalUriNotFound(Exception): 
    def __init__(self, code: ExceptionCodes = ExceptionCodes.ORIGINAL_URI_NOT_FOUND) -> None:
        self.code = code
