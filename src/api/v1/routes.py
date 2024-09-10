from fastapi import APIRouter, Response, Request, Depends

from src.services.auth_service import AuthService
from src.services.db_services import UserDBService
from src.api.v1.dependencies import (
    authorize_dependency, 
    authenticatе_dependency, 
    update_tokens_dependency, 
    logout_dependency,
    current_user_dependency,
    validate_superuser_access,
    AccessToken, 
    RefreshToken,
    SessionDep
)
from src.utils.funcs import refresh_token_expiration_dt, access_token_expiration_dt
from src.utils.DTOs import UserData
from src._types import AccessTokenShema
from src.shemas import CreateUserShema, UpdateUserShema, UserShema, BaseUserShema
 

auth_v1_router = APIRouter(
    prefix="/auth/v1"
)


@auth_v1_router.post("/authorizate")
async def authorizate(
    tokens: tuple[RefreshToken, AccessToken] = Depends(authorize_dependency)
    ) -> Response: 

    response = Response()

    response.set_cookie("refresh_token", tokens[0], samesite="none", secure=True, httponly=True, path="/auth", expires=refresh_token_expiration_dt())
    response.set_cookie("access_token", tokens[1], samesite="none", secure=True, httponly=True, path="/v1", expires=access_token_expiration_dt())

    return response


@auth_v1_router.post("/authenticate")
async def authenticate(access_token: AccessToken = Depends(authenticatе_dependency)) -> Response:
    
    response = Response()

    response.set_cookie("access_token", access_token, samesite="none", secure=True, httponly=True, path="/v1", expires=access_token_expiration_dt())

    return response


@auth_v1_router.post("/update-tokens")
async def update_tokens(tokens: tuple[RefreshToken, AccessToken] = Depends(update_tokens_dependency)) -> Response:
    
    response = Response()

    response.set_cookie("refresh_token", tokens[0], samesite="none", secure=True, httponly=True, path="/auth", expires=refresh_token_expiration_dt())
    response.set_cookie("access_token", tokens[1], samesite="none", secure=True, httponly=True, path="/v1", expires=access_token_expiration_dt())

    return response


@auth_v1_router.post("/validate-access")
async def validate_access(request: Request) -> Response:
    access_token = request.cookies.get("access_token")
    service = AuthService()
    
    if not access_token:
        return Response(
            status_code=401
        )
    elif not service.validate_access_token(access_token):
        return Response(
            "invalid token",
            403
        )
    else:
        access_token = AccessTokenShema.from_token(access_token)

        if access_token.is_expired:
            return Response(
                "token_expired",
                403
            )
        else:
            return Response(
                status_code=200
            )
        

@auth_v1_router.post("/current-user")
async def me(user: UserData | None = Depends(current_user_dependency)) -> BaseUserShema:
    return user


@auth_v1_router.post("/logout", dependencies=[Depends(logout_dependency)])
async def logout() -> Response:
    
    response = Response()

    response.delete_cookie("refresh_token", samesite="none", secure=True, httponly=True)
    response.delete_cookie("access_token", samesite="none", secure=True, httponly=True)

    return response


v1_router = APIRouter(
    prefix="/v1"
)


@v1_router.post("/user", dependencies=[Depends(validate_superuser_access)])
async def create_user(
    session: SessionDep,
    user_data: CreateUserShema,
    user_db_service: UserDBService = Depends(UserDBService)
) -> Response:
    await user_db_service.insert(session, user_data)

    return Response(
        "user successfully created"
    )


@v1_router.get("/user/{ident}", dependencies=[Depends(validate_superuser_access)])
async def get_user(
    ident: str,
    session: SessionDep,
    user_db_service: UserDBService = Depends(UserDBService)
) -> UserShema:

    return await user_db_service.get(session, ident)


@v1_router.patch("/user/{ident}", dependencies=[Depends(validate_superuser_access)])
async def update_user(
    ident: str,
    session: SessionDep,
    user_data: UpdateUserShema,
    user_db_service: UserDBService = Depends(UserDBService)
) -> Response:
    
    await user_db_service.update(session, ident, user_data)

    return Response(
        f"user {ident} successfully updated"
    )


@v1_router.delete("/user/{ident}", dependencies=[Depends(validate_superuser_access)])
async def delete_user(
    ident: str,
    session: SessionDep,
    user_db_service: UserDBService = Depends(UserDBService)
) -> Response:
    
    await user_db_service.delete(session, ident)

    return Response(
        f"user {ident} successfully deleted"
    )
