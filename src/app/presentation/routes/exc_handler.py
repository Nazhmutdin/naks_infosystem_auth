from fastapi import Request
from fastapi.responses import JSONResponse

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


async def user_not_found_handler(
    request: Request,
    exception: UserNotFound
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "code": exception.code,
            "detail": f"user ({exception.ident}) not found"
        }
    )


async def invalid_password_handler(
    request: Request,
    exception: InvalidPassword
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={
            "code": exception.code,
            "detail": "invalid password"
        }
    )


async def invalid_refresh_token_handler(
    request: Request,
    exception: InvalidRefreshToken
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={
            "code": exception.code,
            "detail": "invalid refresh token"
        }
    )


async def invalid_access_token_handler(
    request: Request,
    exception: InvalidAccessToken
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={
            "code": exception.code,
            "detail": "invalid access token"
        }
    )


async def access_forbidden_handler(
    request: Request,
    exception: AccessForbidden
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={
            "code": exception.code,
            "detail": "access forbidden"
        }
    )


async def refresh_token_cookie_not_found_handler(
    request: Request,
    exception: RefreshTokenCookieNotFound
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={
            "code": exception.code,
            "detail": "refresh token cookie not found"
        }
    )


async def access_token_cookie_not_found_handler(
    request: Request,
    exception: AccessTokenCookieNotFound
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={
            "code": exception.code,
            "detail": "access token cookie not found"
        }
    )


async def refresh_token_not_found_handler(
    request: Request,
    exception: RefreshTokenNotFound
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={
            "code": exception.code,
            "detail": f"refresh token ({exception.ident}) not found"
        }
    )


async def refresh_token_revoked_handler(
    request: Request,
    exception: RefreshTokenRevoked
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={
            "code": exception.code,
            "detail": "refresh token revoked"
        }
    )


async def refresh_token_expired_handler(
    request: Request,
    exception: RefreshTokenExpired
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={
            "code": exception.code,
            "detail": "refresh token expired"
        }
    )


async def permission_data_not_found_handler(
    request: Request,
    exception: PermissionDataNotFound
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={
            "code": exception.code,
            "detail": f"internal error; permissions for user ({exception.user_ident}) don't exist"
        }
    )

async def original_method_not_found_handler(
    request: Request,
    exception: OriginalMethodNotFound
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "code": exception.code,
            "detail": "internal error; original method header doesn't present"
        }
    )

async def original_uri_not_found_handler(
    request: Request,
    exception: OriginalUriNotFound
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "code": exception.code,
            "detail": "internal error; original uri header doesn't present"
        }
    )

