from uuid import UUID, uuid4

from pydantic import BaseModel
from fastapi import HTTPException, Request, Depends

from src.shemas import *
from src.database import get_session
from src.services.auth_service import AuthService
from src.services.db_services import UserDBService, RefreshTokenDBService
from src.utils.funcs import current_utc_datetime, current_utc_datetime_without_timezone, refresh_token_expiration_dt_without_timezone


class AuthData(BaseModel):
    password: str
    login: str


type AccessToken = str
type RefreshToken = str


async def get_user(auth_data: AuthData, session = Depends(get_session)) -> UserShema:
    
    service = AuthService()
    user = await UserDBService(session).get(auth_data.login)

    if not user:
        raise HTTPException(
            400,
            f"user ({auth_data.login}) not found",
        )
    
    if not service.validate_password(auth_data.password, user.hashed_password):
        raise HTTPException(
            400,
            f"Invalid password",
        )

    return user


async def validate_refresh_token(request: Request, session = Depends(get_session)) -> RefreshTokenShema:
    
    service = RefreshTokenDBService(session)

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            400,
            "refresh token required"
        )
    
    refresh_token = await service.get(refresh_token)

    if not refresh_token:
        raise HTTPException(
            400,
            "refresh token not found"
        )
    
    if refresh_token.revoked:
        await service.revoke_all_user_tokens(refresh_token.user_ident)

        raise HTTPException(
            400,
            "revoked token"
        )
    
    return refresh_token


async def create_access_token(user_ident: str | UUID) -> AccessToken:
    
    auth_service = AuthService()
    gen_dt = current_utc_datetime()

    token = auth_service.create_access_token(
        user_ident=user_ident.hex,
        gen_dt=gen_dt
    )

    return token


async def create_refresh_token(user_ident: str | UUID) -> CreateRefreshTokenShema:
    
    auth_service = AuthService()

    gen_dt = current_utc_datetime_without_timezone()
    exp_dt = refresh_token_expiration_dt_without_timezone()

    token_ident = uuid4()

    token = auth_service.create_refresh_token(
        user_ident=user_ident.hex,
        ident=token_ident,
        gen_dt=gen_dt,
        exp_dt=exp_dt
    )

    token = CreateRefreshTokenShema(
        ident=token_ident,
        user_ident=user_ident,
        token=token,
        gen_dt=gen_dt,
        exp_dt=exp_dt
    )

    return token


async def authorize_dependency(user: UserShema = Depends(get_user), session = Depends(get_session)) -> tuple[RefreshToken, AccessToken]:
    service = RefreshTokenDBService(session)

    await service.revoke_all_user_tokens(user.ident)

    refresh_token = await create_refresh_token(user.ident)
    access_token = await create_access_token(user.ident)

    await service.add(refresh_token)

    return (refresh_token.token, access_token)


async def authenticatе_dependency(
    refresh_token: RefreshTokenShema = Depends(validate_refresh_token), 
    session = Depends(get_session)
    ) -> AccessToken:

    if refresh_token.expired:
        raise HTTPException(
            400,
            "refresh token expired"
        )

    service = UserDBService(session)
    auth_service = AuthService()

    user = await service.get(
        auth_service.read_token(refresh_token.token)["user_ident"]
    )

    if not user:
        raise HTTPException(
            400, 
            "user not found"
        )

    access_token = await create_access_token(user.ident)

    return access_token


async def update_tokens_dependency(
    refresh_token: RefreshTokenShema = Depends(validate_refresh_token),
    session = Depends(get_session)
    ) -> tuple[RefreshToken, AccessToken]:
    
    service = RefreshTokenDBService(session)
    
    await service.revoke_all_user_tokens(
        refresh_token.user_ident
    )

    refresh_token = await create_refresh_token(refresh_token.user_ident)
    access_token = await create_access_token(refresh_token.user_ident)

    await service.add(refresh_token)

    return (refresh_token.token, access_token)
