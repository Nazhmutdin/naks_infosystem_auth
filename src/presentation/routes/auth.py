from datetime import timezone

from fastapi import APIRouter, Response

from src.presentation.shemas import UserWithouPasswordShema
from src.infrastructure.dto import LoginData
from src.main.dependencies import (
    LoginUserInteractorDep,
    AuthenticateUserInteractorDep,
    UpdateUserTokensInteractorDep,
    LogoutUserInteractorDep,
    ValidateAccessInteractorDep,
    CurrentUserDep,
    RefreshTokenDep,
    AccessTokenDep
)
 

auth_router = APIRouter(
    prefix="/auth/v1"
)


@auth_router.post("/login")
async def login(
    login_action: LoginUserInteractorDep,
    data: LoginData
) -> Response: 
    
    refresh_token, access_token = await login_action(data)

    response = Response()

    response.set_cookie("refresh_token", refresh_token.token, samesite="none", secure=True, httponly=True, path="/auth", expires=refresh_token.exp_dt.replace(tzinfo=timezone.utc))
    response.set_cookie("access_token", access_token.token, samesite="none", secure=True, httponly=True, path="/v1", expires=access_token.exp_dt.replace(tzinfo=timezone.utc))

    return response


@auth_router.post("/authenticate")
async def authenticate(
    authenticate_action: AuthenticateUserInteractorDep,
    refresh_token: RefreshTokenDep
) -> Response:
    
    access_token = await authenticate_action(refresh_token)
    
    response = Response()

    response.set_cookie("access_token", access_token.token, samesite="none", secure=True, httponly=True, path="/v1", expires=access_token.exp_dt.replace(tzinfo=timezone.utc))

    return response


@auth_router.post("/update-tokens")
async def update_tokens(
    update_tokens_action: UpdateUserTokensInteractorDep,
    refresh_token: RefreshTokenDep
) -> Response:
    
    new_refresh_token, new_access_token = await update_tokens_action(refresh_token)
    
    response = Response()

    response.set_cookie("refresh_token", new_refresh_token.token, samesite="none", secure=True, httponly=True, path="/auth", expires=new_refresh_token.exp_dt.replace(tzinfo=timezone.utc))
    response.set_cookie("access_token", new_access_token.token, samesite="none", secure=True, httponly=True, path="/v1", expires=new_access_token.exp_dt.replace(tzinfo=timezone.utc))

    return response


@auth_router.post("/validate-access")
async def validate_access(
    validate_access_action: ValidateAccessInteractorDep,
    access_token: AccessTokenDep
) -> Response:
    
    await validate_access_action(access_token)
    
    response = Response()

    return response
        

@auth_router.post("/me")
async def me(user: CurrentUserDep) -> UserWithouPasswordShema:
    return user


@auth_router.post("/logout")
async def logout(
    logout_action: LogoutUserInteractorDep,
    refresh_token: RefreshTokenDep
) -> Response:
    
    await logout_action(refresh_token)
    
    response = Response()

    response.delete_cookie("refresh_token", samesite="none", secure=True, httponly=True)
    response.delete_cookie("access_token", samesite="none", secure=True, httponly=True)

    return response
