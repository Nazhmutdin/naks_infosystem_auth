import typing as t
from uuid import UUID
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker
from fastapi import Request, Depends
from naks_library.commiter import SqlAlchemyCommitter
from jose.exceptions import JWTError, JWTClaimsError

from src.application.interfaces.gateways import UserGateway, RefreshTokenGateway
from src.application.dto import UserDTO
from src.application.common.exc import (
    CurrentUserNotFound,
    AccessForbidden,
    RefreshTokenCookieNotFound,
    AccessTokenCookieNotFound,
    RefreshTokenNotFound,
    InvalidRefreshToken,
    InvalidAccessToken
)
from src.application.interactors.user import (
    CreateUserInteractor, 
    GetUserInteractor, 
    UpdateUserInteractor, 
    DeleteUserInteractor
)
from src.application.interactors.refresh_token import (
    CreateRefreshTokenInteractor, 
    GetRefreshTokenInteractor, 
    UpdateRefreshTokenInteractor, 
    DeleteRefreshTokenInteractor
)
from src.application.interactors.auth import (
    LoginUserInteractor, 
    AuthenticateUserInteractor, 
    UpdateUserTokensInteractor,
    LogoutUserInteractor,
    ValidateAccessInteractor
)
from src.infrastructure.database.mappers import UserMapper, RefreshTokenMapper
from src.infrastructure.database.setup import create_engine, create_session_maker
from src.infrastructure.services.jwt_service import JwtService
from src.infrastructure.dto import AccessTokenDTO, RefreshTokenDTO


class AppContainer:

    @property
    @lru_cache
    def engine(self) -> AsyncEngine:
        return create_engine()


    @property
    @lru_cache
    def session_maker(self) -> async_sessionmaker[AsyncSession]:
        return create_session_maker(self.engine)


    async def get_session(self):
        async with self.session_maker() as session:
            yield session

    
    def get_jwt_service(self) -> JwtService:
        return JwtService()


container = AppContainer()
SessionDep = t.Annotated[AsyncSession, Depends(container.get_session)]
JwtServiceDep = t.Annotated[JwtService, Depends(container.get_jwt_service)]

def get_user_gateway(session: AsyncSession) -> UserGateway:
    return UserMapper(session)


async def dump_create_user_interactor(session: SessionDep):
    commiter = SqlAlchemyCommitter(session)
    gateway = get_user_gateway(session)

    return CreateUserInteractor(
        gateway=gateway,
        commiter=commiter
    )


async def dump_get_user_interactor(session: SessionDep):
    gateway = get_user_gateway(session)

    return GetUserInteractor(
        gateway=gateway
    )


async def dump_update_user_interactor(session: SessionDep):
    commiter = SqlAlchemyCommitter(session)
    gateway = get_user_gateway(session)

    return UpdateUserInteractor(
        gateway=gateway,
        commiter=commiter
    )


async def dump_delete_user_interactor(session: SessionDep):
    commiter = SqlAlchemyCommitter(session)
    gateway = get_user_gateway(session)

    return DeleteUserInteractor(
        gateway=gateway,
        commiter=commiter
    )


CreateUserInteractorDep = t.Annotated[CreateUserInteractor, Depends(dump_create_user_interactor)]
GetUserInteractorDep = t.Annotated[GetUserInteractor, Depends(dump_get_user_interactor)]
UpdateUserInteractorDep = t.Annotated[UpdateUserInteractor, Depends(dump_update_user_interactor)]
DeleteUserInteractorDep = t.Annotated[DeleteUserInteractor, Depends(dump_delete_user_interactor)]


def get_refresh_token_gateway(session: AsyncSession) -> RefreshTokenGateway:
    return RefreshTokenMapper(session)


async def dump_create_refresh_token_interactor(session: SessionDep):
    commiter = SqlAlchemyCommitter(session)
    gateway = get_refresh_token_gateway(session)

    return CreateRefreshTokenInteractor(
        gateway=gateway,
        commiter=commiter
    )


async def dump_get_refresh_token_interactor(session: SessionDep):
    gateway = get_refresh_token_gateway(session)

    return GetRefreshTokenInteractor(
        gateway=gateway
    )


async def dump_update_refresh_token_interactor(session: SessionDep):
    commiter = SqlAlchemyCommitter(session)
    gateway = get_refresh_token_gateway(session)

    return UpdateRefreshTokenInteractor(
        gateway=gateway,
        commiter=commiter
    )


async def dump_delete_refresh_token_interactor(session: SessionDep):
    commiter = SqlAlchemyCommitter(session)
    gateway = get_refresh_token_gateway(session)

    return DeleteRefreshTokenInteractor(
        gateway=gateway,
        commiter=commiter
    )


CreateRefreshTokenInteractorDep = t.Annotated[CreateRefreshTokenInteractor, Depends(dump_create_refresh_token_interactor)]
GetRefreshTokenInteractorDep = t.Annotated[GetRefreshTokenInteractor, Depends(dump_get_refresh_token_interactor)]
UpdateRefreshTokenInteractorDep = t.Annotated[UpdateRefreshTokenInteractor, Depends(dump_update_refresh_token_interactor)]
DeleteRefreshTokenInteractorDep = t.Annotated[DeleteRefreshTokenInteractor, Depends(dump_delete_refresh_token_interactor)]


async def get_refresh_token(request: Request, jwt_service: JwtServiceDep, get: GetRefreshTokenInteractorDep) -> RefreshTokenDTO:
    refresh_token_cookie = request.cookies.get("refresh_token")

    if refresh_token_cookie:
        try:
            refresh_token_payload = jwt_service.read_refresh_token(refresh_token_cookie)
        except (JWTError, JWTClaimsError):
            raise InvalidRefreshToken
        
        token_ident = UUID(refresh_token_payload["ident"])

        res = await get(token_ident)

        if res:
            return res
        
        raise RefreshTokenNotFound(token_ident)
    
    raise RefreshTokenCookieNotFound


async def get_access_token(request: Request, jwt_service: JwtServiceDep) -> AccessTokenDTO:
    access_token_cookie = request.cookies.get("access_token")

    if access_token_cookie:
        try:
            access_token_payload = jwt_service.read_access_token(access_token_cookie)
        except (JWTError, JWTClaimsError):
            raise InvalidAccessToken

        return AccessTokenDTO(
            token=access_token_cookie,
            user_ident=access_token_payload["user_ident"],
            gen_dt=access_token_payload["gen_dt"],
            exp_dt=access_token_payload["exp_dt"]
        )
        
    
    raise AccessTokenCookieNotFound


RefreshTokenDep = t.Annotated[RefreshTokenDTO, Depends(get_refresh_token)]
AccessTokenDep = t.Annotated[AccessTokenDTO, Depends(get_access_token)]


async def get_current_user(access_token: AccessTokenDep, get_user: GetUserInteractorDep) -> UserDTO:
    user = await get_user(access_token.user_ident)

    if user:
        return user
    
    raise CurrentUserNotFound(
        user_ident=access_token.user_ident,
        access_token=access_token.token
    )
        

CurrentUserDep = t.Annotated[UserDTO, Depends(get_current_user)]


async def check_user_crud_action_access(user: CurrentUserDep):
    if not user.is_superuser:
        raise AccessForbidden()


async def dump_login_user_interactor(session: SessionDep, jwt_service: JwtServiceDep):
    user_gateway = get_user_gateway(session)
    refresh_token_gateway = get_refresh_token_gateway(session)
    commiter = SqlAlchemyCommitter(session)

    return LoginUserInteractor(
        user_gateway=user_gateway,
        refresh_token_gateway=refresh_token_gateway,
        commiter=commiter,
        jwt_service=jwt_service
    )


async def dump_authenticate_user_interactor(session: SessionDep, jwt_service: JwtServiceDep):
    user_gateway = get_user_gateway(session)
    refresh_token_gateway = get_refresh_token_gateway(session)
    commiter = SqlAlchemyCommitter(session)

    return AuthenticateUserInteractor(
        user_gateway=user_gateway,
        refresh_token_gateway=refresh_token_gateway,
        commiter=commiter,
        jwt_service=jwt_service
    )


async def dump_update_user_tokens_interactor(session: SessionDep, jwt_service: JwtServiceDep):
    user_gateway = get_user_gateway(session)
    refresh_token_gateway = get_refresh_token_gateway(session)
    commiter = SqlAlchemyCommitter(session)

    return UpdateUserTokensInteractor(
        user_gateway=user_gateway,
        refresh_token_gateway=refresh_token_gateway,
        commiter=commiter,
        jwt_service=jwt_service
    )


async def dump_logout_user_interactor(session: SessionDep):
    refresh_token_gateway = get_refresh_token_gateway(session)
    commiter = SqlAlchemyCommitter(session)

    return LogoutUserInteractor(
        refresh_token_gateway=refresh_token_gateway,
        commiter=commiter
    )


async def validate_access_interactor():

    return ValidateAccessInteractor()


LoginUserInteractorDep = t.Annotated[LoginUserInteractor, Depends(dump_login_user_interactor)]
AuthenticateUserInteractorDep = t.Annotated[AuthenticateUserInteractor, Depends(dump_authenticate_user_interactor)]
UpdateUserTokensInteractorDep = t.Annotated[UpdateUserTokensInteractor, Depends(dump_update_user_tokens_interactor)]
LogoutUserInteractorDep = t.Annotated[LogoutUserInteractor, Depends(dump_logout_user_interactor)]
ValidateAccessInteractorDep = t.Annotated[ValidateAccessInteractor, Depends(validate_access_interactor)]
