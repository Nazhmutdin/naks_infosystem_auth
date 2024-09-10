from uuid import UUID, uuid4
import typing as t

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Request, Depends

from src.shemas import CreateRefreshTokenShema
from src.utils.DTOs import RefreshTokenData, UserData, AccessTokenData
from src.database import get_session
from src.services.auth_service import AuthService
from src.services.db_services import UserDBService, RefreshTokenDBService
from src.utils.funcs import current_utc_datetime, current_utc_datetime_without_timezone, refresh_token_expiration_dt_without_timezone


class AuthData(BaseModel):
    password: str
    login: str


type AccessToken = str
type RefreshToken = str


SessionDep = t.Annotated[AsyncSession, Depends(get_session)]


async def get_user(auth_data: AuthData, session: SessionDep, user_db_service: UserDBService = Depends(UserDBService)) -> UserData:
    
    service = AuthService()
    user = await user_db_service.get_by_login(session, auth_data.login)

    if not user:
        raise HTTPException(
            403,
            f"user ({auth_data.login}) not found",
        )
    
    if not service.validate_password(auth_data.password, user.hashed_password):
        raise HTTPException(
            403,
            f"Invalid password",
        )

    return user


async def validate_refresh_token(
    request: Request, 
    session: SessionDep, 
    refresh_token_db_service: RefreshTokenDBService = Depends(RefreshTokenDBService)
) -> RefreshTokenData:

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            401,
            "refresh token required"
        )
    
    refresh_token = await refresh_token_db_service.get_by_token(session, refresh_token)

    if not refresh_token:
        raise HTTPException(
            403,
            "refresh token not found"
        )
    
    if refresh_token.revoked:
        await refresh_token_db_service.revoke_all_user_tokens(session, refresh_token.user_ident)

        raise HTTPException(
            403,
            "revoked token"
        )
    
    return refresh_token


async def validate_access_token(request: Request) -> AccessTokenData:

    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(
            401,
            "access token required"
        )

    auth_service = AuthService()

    return AccessTokenData(**auth_service.read_token(access_token), token=access_token)


async def validate_superuser_access(
    session: SessionDep,
    user_db_service: UserDBService = Depends(UserDBService),
    access_token: AccessTokenData = Depends(validate_access_token)
) -> None:

    user = await user_db_service.get(session, access_token.user_ident)

    if not user.is_superuser:
        raise HTTPException(
            403,
            f"user ({user.login}) is not superuser"
        )


async def create_access_token(user_ident: str | UUID) -> AccessTokenData:
    
    auth_service = AuthService()
    gen_dt = current_utc_datetime()

    token = auth_service.create_access_token(
        user_ident=user_ident.hex,
        gen_dt=gen_dt
    )

    return AccessTokenData(
        gen_dt=gen_dt,
        user_ident=user_ident,
        token=token
    )


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
    session: SessionDep, 
    refresh_token_db_service: RefreshTokenDBService = Depends(RefreshTokenDBService),
    user: UserData = Depends(get_user)
) -> tuple[RefreshToken, AccessToken]:

    await refresh_token_db_service.revoke_all_user_tokens(session, user.ident)

    refresh_token = await create_refresh_token(user.ident)
    access_token = await create_access_token(user.ident)

    await refresh_token_db_service.insert(session, refresh_token)

    return (refresh_token.token, access_token.token)


async def authenticatе_dependency(
    session: SessionDep, 
    user_db_service: UserDBService = Depends(UserDBService),
    refresh_token: RefreshTokenData = Depends(validate_refresh_token)
) -> AccessToken:

    if refresh_token.expired:
        raise HTTPException(
            403,
            "refresh token expired"
        )

    auth_service = AuthService()

    user = await user_db_service.get(
        session,
        auth_service.read_token(refresh_token.token)["user_ident"]
    )

    if not user:
        raise HTTPException(
            403, 
            f"user ({refresh_token.user_ident}) not found",
        )

    access_token = await create_access_token(user.ident)

    return access_token.token


async def update_tokens_dependency(
    session: SessionDep,
    refresh_token_db_service: RefreshTokenDBService = Depends(RefreshTokenDBService),
    refresh_token: RefreshTokenData = Depends(validate_refresh_token)
) -> tuple[RefreshToken, AccessToken]:
    
    await refresh_token_db_service.revoke_all_user_tokens(
        session,
        refresh_token.user_ident
    )

    refresh_token = await create_refresh_token(refresh_token.user_ident)
    access_token = await create_access_token(refresh_token.user_ident)

    await refresh_token_db_service.insert(session, refresh_token)

    return (refresh_token.token, access_token.token)


async def logout_dependency(
    session: SessionDep,
    refresh_token_db_service: RefreshTokenDBService = Depends(RefreshTokenDBService),
    refresh_token: RefreshTokenData = Depends(validate_refresh_token)
) -> None:

    await refresh_token_db_service.revoke_all_user_tokens(
        session,
        refresh_token.user_ident
    )


async def current_user_dependency(
    session: SessionDep,
    user_db_service: UserDBService = Depends(UserDBService),
    refresh_token: RefreshTokenData = Depends(validate_refresh_token)
) -> UserData:
    user = await user_db_service.get(session, refresh_token.user_ident)

    if user is None:
        raise HTTPException(
            403,
            f"user ({refresh_token.user_ident}) not found",
        )
    
    return user
