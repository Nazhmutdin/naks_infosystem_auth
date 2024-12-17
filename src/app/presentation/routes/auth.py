from datetime import timezone

from fastapi import APIRouter, Response, Request
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute

from app.presentation.shemas import UserWithouPasswordShema
from app.infrastructure.dto import LoginData, AccessTokenDTO
from app.application.dto import RefreshTokenDTO, CurrentUser, PermissionDTO
from app.application.interactors import (
    LoginUserInteractor,
    AuthenticateUserInteractor,
    UpdateUserTokensInteractor,
    LogoutUserInteractor,
    ValidateAccessInteractor,
    GetUserPermissionsInteractor,
)
from app.application.common.exc import PermissionDataNotFound
from app.config import ApplicationConfig


auth_router = APIRouter(
    prefix="/auth/v1",
    route_class=DishkaRoute
)


@auth_router.post("/login")
async def login(
    login_action: FromDishka[LoginUserInteractor],
    data: LoginData
) -> Response: 
    
    refresh_token, access_token = await login_action(data)

    response = Response()

    response.set_cookie("refresh_token", refresh_token.token, domain=ApplicationConfig.DOMAIN(), samesite="strict", secure=True, httponly=True, path="/auth", expires=refresh_token.exp_dt.replace(tzinfo=timezone.utc))
    response.set_cookie("access_token", access_token.token, domain=ApplicationConfig.DOMAIN(), samesite="strict", secure=True, httponly=True, expires=access_token.exp_dt.replace(tzinfo=timezone.utc))

    return response


@auth_router.post("/authenticate")
async def authenticate(
    authenticate_action: FromDishka[AuthenticateUserInteractor],
    refresh_token: FromDishka[RefreshTokenDTO]
) -> Response:
    
    access_token = await authenticate_action(refresh_token)
    
    response = Response()

    response.set_cookie("access_token", access_token.token, domain=ApplicationConfig.DOMAIN(), samesite="strict", secure=True, httponly=True, expires=access_token.exp_dt.replace(tzinfo=timezone.utc))

    return response


@auth_router.post("/update-tokens")
async def update_tokens(
    update_tokens_action: FromDishka[UpdateUserTokensInteractor],
    refresh_token: FromDishka[RefreshTokenDTO]
) -> Response:
    
    new_refresh_token, new_access_token = await update_tokens_action(refresh_token)
    
    response = Response()

    response.set_cookie("refresh_token", new_refresh_token.token, domain=ApplicationConfig.DOMAIN(), samesite="strict", secure=True, httponly=True, path="/auth", expires=new_refresh_token.exp_dt.replace(tzinfo=timezone.utc))
    response.set_cookie("access_token", new_access_token.token, domain=ApplicationConfig.DOMAIN(), samesite="strict", secure=True, httponly=True, expires=new_access_token.exp_dt.replace(tzinfo=timezone.utc))

    return response


@auth_router.post("/logout")
async def logout(
    logout_action: FromDishka[LogoutUserInteractor],
    refresh_token: FromDishka[RefreshTokenDTO]
) -> Response:
    
    await logout_action(refresh_token)
    
    response = Response()

    response.delete_cookie("refresh_token", domain=ApplicationConfig.DOMAIN(), path="/auth", samesite="strict", secure=True, httponly=True)
    response.delete_cookie("access_token", domain=ApplicationConfig.DOMAIN(), samesite="strict", secure=True, httponly=True)

    return response


@auth_router.post("/validate-access")
async def validate_data_access(
    validate_access_action: FromDishka[ValidateAccessInteractor],
    access_token: FromDishka[AccessTokenDTO],
    request: Request
) -> Response:
    
    await validate_access_action(
        access_token=access_token, 
        request=request
    )
    
    response = Response()

    return response


@auth_router.post("/me/permissions")
async def permissions(
    user: FromDishka[CurrentUser],
    get_permissions: FromDishka[GetUserPermissionsInteractor]
) -> PermissionDTO:
    res =  await get_permissions(user)
    
    if not res:
        raise PermissionDataNotFound(user_ident=user.ident)
    
    return res


@auth_router.post("/me")
async def me(user: FromDishka[CurrentUser]) -> UserWithouPasswordShema:
    return user
