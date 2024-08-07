from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Request, Depends

from src.shemas import CreateRefreshTokenShema
from src.utils.DTOs import RefreshTokenData, UserData
from src.database import get_session
from src.services.auth_service import AuthService
from src.services.db_services import UserDBService, RefreshTokenDBService
from src.utils.funcs import current_utc_datetime, current_utc_datetime_without_timezone, refresh_token_expiration_dt_without_timezone


class AuthData(BaseModel):
    password: str
    login: str


type AccessToken = str
type RefreshToken = str


async def get_user_db_service(session: AsyncSession = Depends(get_session)) -> UserDBService:
    return UserDBService(session)


async def get_refresh_token_db_service(session: AsyncSession = Depends(get_session)) -> RefreshTokenDBService:
    return RefreshTokenDBService(session)


async def get_user(auth_data: AuthData, user_db_service: UserDBService = Depends(get_user_db_service)) -> UserData:
    
    service = AuthService()
    user = await user_db_service.get(auth_data.login)

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


async def validate_refresh_token(request: Request, refresh_token_db_service: RefreshTokenDBService = Depends(get_refresh_token_db_service)) -> RefreshTokenData:

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            400,
            "refresh token required"
        )
    
    refresh_token = await refresh_token_db_service.get(refresh_token)

    if not refresh_token:
        raise HTTPException(
            400,
            "refresh token not found"
        )
    
    if refresh_token.revoked:
        await refresh_token_db_service.revoke_all_user_tokens(refresh_token.user_ident)

        raise HTTPException(
            400,
            "revoked token"
        )
    
    return refresh_token


async def validate_superuser_access(
    refresh_token: RefreshTokenData = Depends(validate_refresh_token),
    user_db_service: UserDBService = Depends(get_user_db_service)
) -> None:

    user = await user_db_service.get(refresh_token.user_ident)

    if not user.is_superuser:
        raise HTTPException(
            403,
            f"user ({user.login}) is not superuser"
        )


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


async def authorize_dependency(
    user: UserData = Depends(get_user), 
    refresh_token_db_service: RefreshTokenDBService = Depends(get_refresh_token_db_service)
) -> tuple[RefreshToken, AccessToken]:

    await refresh_token_db_service.revoke_all_user_tokens(user.ident)

    refresh_token = await create_refresh_token(user.ident)
    access_token = await create_access_token(user.ident)

    await refresh_token_db_service.add(refresh_token)

    return (refresh_token.token, access_token)


async def authenticatе_dependency(
    refresh_token: RefreshTokenData = Depends(validate_refresh_token), 
    user_db_service: UserDBService = Depends(get_user_db_service)
) -> AccessToken:

    if refresh_token.expired:
        raise HTTPException(
            400,
            "refresh token expired"
        )

    auth_service = AuthService()

    user = await user_db_service.get(
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
    refresh_token: RefreshTokenData = Depends(validate_refresh_token),
    refresh_token_db_service: RefreshTokenDBService = Depends(get_refresh_token_db_service)
) -> tuple[RefreshToken, AccessToken]:
    
    await refresh_token_db_service.revoke_all_user_tokens(
        refresh_token.user_ident
    )

    refresh_token = await create_refresh_token(refresh_token.user_ident)
    access_token = await create_access_token(refresh_token.user_ident)

    await refresh_token_db_service.add(refresh_token)

    return (refresh_token.token, access_token)


async def logout_dependency(
    refresh_token: RefreshTokenData = Depends(validate_refresh_token),
    refresh_token_db_service: RefreshTokenDBService = Depends(get_refresh_token_db_service)
) -> None:

    await refresh_token_db_service.revoke_all_user_tokens(
        refresh_token.user_ident
    )


async def current_user_dependency(
    refresh_token: RefreshTokenData = Depends(validate_refresh_token),
    user_db_service: UserDBService = Depends(get_user_db_service)
) -> UserData:
    user = await user_db_service.get(refresh_token.user_ident)

    if user is None:
        raise HTTPException(
            404,
            "user not found"
        )
    
    return user
