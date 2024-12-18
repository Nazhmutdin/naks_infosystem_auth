from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka

from app.main.dependencies.ioc_container import container
from app.application.common.exc import (
    AccessForbidden, 
    UserNotFound, 
    RefreshTokenCookieNotFound, 
    AccessTokenCookieNotFound, 
    RefreshTokenNotFound,
    InvalidPassword,
    InvalidRefreshToken,
    RefreshTokenRevoked,
    RefreshTokenExpired,
    InvalidAccessToken,
    PermissionDataNotFound,
    OriginalMethodNotFound,
    OriginalUriNotFound
)
from app.presentation.routes.user import user_router
from app.presentation.routes.auth import auth_router
from app.presentation.routes.exc_handler import (
    user_not_found_handler,
    access_forbidden_handler,
    refresh_token_cookie_not_found_handler,
    access_token_cookie_not_found_handler,
    refresh_token_not_found_handler,
    invalid_password_handler,
    invalid_refresh_token_handler,
    refresh_token_revoked_handler,
    refresh_token_expired_handler,
    invalid_access_token_handler,
    permission_data_not_found_handler,
    original_method_not_found_handler,
    original_uri_not_found_handler
)

app = FastAPI()

setup_dishka(container=container, app=app)

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
app.add_exception_handler(PermissionDataNotFound, permission_data_not_found_handler)
app.add_exception_handler(OriginalMethodNotFound, original_method_not_found_handler)
app.add_exception_handler(OriginalUriNotFound, original_uri_not_found_handler)

app.include_router(user_router)
app.include_router(auth_router)
