from uuid import UUID


class CurrentUserNotFound(Exception):
    def __init__(
        self, 
        user_ident: UUID, 
        access_token: str
    ) -> None:
        self.user_ident = user_ident
        self.access_token = access_token


class AccessForbidden(Exception): ...


class UserNotFound(Exception):
    def __init__(
        self, 
        ident: UUID | str,
    ) -> None:
        self.ident = ident


class InvalidPassword(Exception): ...


class InvalidRefreshToken(Exception): ...


class InvalidAccessToken(Exception): ...


class RefreshTokenCookieNotFound(Exception): ...


class AccessTokenCookieNotFound(Exception): ...


class RefreshTokenNotFound(Exception):
    def __init__(
        self, 
        ident: UUID,
    ) -> None:
        self.ident = ident


class RefreshTokenRevoked(Exception): ...


class RefreshTokenExpired(Exception): ...


class AccessTokenExpired(Exception): ...
