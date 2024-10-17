from fastapi import FastAPI

from app.application.common.exc import (
    CurrentUserNotFound, 
    AccessForbidden, 
    UserNotFound, 
    RefreshTokenCookieNotFound, 
    AccessTokenCookieNotFound, 
    RefreshTokenNotFound,
    InvalidPassword,
    InvalidRefreshToken,
    RefreshTokenRevoked,
    RefreshTokenExpired,
    InvalidAccessToken
)
from app.presentation.routes.user import user_router
from app.presentation.routes.auth import auth_router
from app.presentation.routes.exc_handler import (
    current_user_not_found_handler,
    user_not_found_handler,
    access_forbidden_handler,
    refresh_token_cookie_not_found_handler,
    access_token_cookie_not_found_handler,
    refresh_token_not_found_handler,
    invalid_password_handler,
    invalid_refresh_token_handler,
    refresh_token_revoked_handler,
    refresh_token_expired_handler,
    invalid_access_token_handler
)


def register_routes(app: FastAPI):
    app.add_exception_handler(CurrentUserNotFound, current_user_not_found_handler)
    app.add_exception_handler(AccessForbidden, access_forbidden_handler)
    app.add_exception_handler(UserNotFound, user_not_found_handler)
    app.add_exception_handler(RefreshTokenCookieNotFound, refresh_token_cookie_not_found_handler)
    app.add_exception_handler(AccessTokenCookieNotFound, access_token_cookie_not_found_handler)
    app.add_exception_handler(RefreshTokenNotFound, refresh_token_not_found_handler)
    app.add_exception_handler(InvalidPassword, invalid_password_handler)
    app.add_exception_handler(InvalidRefreshToken, invalid_refresh_token_handler)
    app.add_exception_handler(RefreshTokenRevoked, refresh_token_revoked_handler)
    app.add_exception_handler(RefreshTokenExpired, refresh_token_expired_handler)
    app.add_exception_handler(InvalidAccessToken, invalid_access_token_handler)

    app.include_router(user_router)
    app.include_router(auth_router)