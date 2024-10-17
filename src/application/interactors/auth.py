from uuid import uuid4
from datetime import timedelta, datetime

from naks_library.interfaces import ICommitter

from src.application.interfaces.gateways import UserGateway, RefreshTokenGateway
from src.application.common.exc import UserNotFound, InvalidPassword, RefreshTokenRevoked, AccessTokenExpired
from src.application.dto import UserDTO
from infrastructure.dto import AccessTokenDTO, RefreshTokenDTO, LoginData, convert_refresh_token_dto_to_create_refresh_token_dto
from src.infrastructure.services.jwt_service import JwtService
from src.infrastructure.services.hasher import PasswordHasher
from src.configs import ApplicationConfig


def gen_new_refresh_token(user: UserDTO, jwt_service: JwtService) -> RefreshTokenDTO:

    refresh_token_ident = uuid4()
    gen_dt = datetime.now()
    exp_dt = gen_dt + timedelta(minutes=ApplicationConfig.REFRESH_TOKEN_LIFETIME_HOURS())

    refresh_token = jwt_service.create_refresh_token(
        ident=refresh_token_ident,
        user_ident=user.ident,
        gen_dt=gen_dt,
        exp_dt=exp_dt
    )

    return RefreshTokenDTO(
        ident=refresh_token_ident,
        user_ident=user.ident,
        token=refresh_token,
        revoked=False,
        gen_dt=gen_dt,
        exp_dt=exp_dt
    )


def gen_new_access_token(user: UserDTO, jwt_service: JwtService) -> AccessTokenDTO:
        
    gen_dt = datetime.now()
    exp_dt = gen_dt + timedelta(minutes=ApplicationConfig.ACCESS_TOKEN_LIFETIME_MINUTES())

    access_token = jwt_service.create_access_token(
        user_ident=user.ident,
        gen_dt=gen_dt,
        exp_dt=exp_dt
    )

    return AccessTokenDTO(
        token=access_token,
        user_ident=user.ident,
        gen_dt=gen_dt,
        exp_dt=exp_dt
    )


class LoginUserInteractor:
    def __init__(
        self,
        user_gateway: UserGateway,
        refresh_token_gateway: RefreshTokenGateway,
        commiter: ICommitter,
        jwt_service: JwtService
    ) -> None:
        self.user_gateway = user_gateway
        self.refresh_token_gateway = refresh_token_gateway
        self.commiter = commiter
        self.jwt_service = jwt_service
        

    async def __call__(self, data: LoginData) -> tuple[RefreshTokenDTO, AccessTokenDTO]:
        user = await self.user_gateway.get_by_login(data.login)

        if not user:
            raise UserNotFound(data.login)

        if not PasswordHasher().verify(data.password, user.hashed_password):
            raise InvalidPassword
        
        await self.refresh_token_gateway.revoke_all_user_tokens(user.ident)

        refresh_token = gen_new_refresh_token(user, self.jwt_service)
        access_token = gen_new_access_token(user, self.jwt_service)

        await self.refresh_token_gateway.insert(convert_refresh_token_dto_to_create_refresh_token_dto(refresh_token))

        await self.commiter.commit()

        return (refresh_token, access_token)


class AuthenticateUserInteractor:
    def __init__(
        self,
        user_gateway: UserGateway,
        refresh_token_gateway: RefreshTokenGateway,
        commiter: ICommitter,
        jwt_service: JwtService
    ) -> None:
        self.user_gateway = user_gateway
        self.refresh_token_gateway = refresh_token_gateway
        self.commiter = commiter
        self.jwt_service = jwt_service

    
    async def __call__(self, refresh_token: RefreshTokenDTO) -> AccessTokenDTO:
        
        user = await self.user_gateway.get(refresh_token.user_ident)

        if not user:
            raise UserNotFound(refresh_token.user_ident)
        

        if refresh_token.revoked:
            await self.refresh_token_gateway.revoke_all_user_tokens(user.ident)

            raise RefreshTokenRevoked
        

        if refresh_token.expired:
            await self.refresh_token_gateway.revoke_all_user_tokens(user.ident)

            raise RefreshTokenRevoked

        await self.commiter.commit()

        return gen_new_access_token(user, self.jwt_service)
        

class UpdateUserTokensInteractor:
    def __init__(
        self,
        user_gateway: UserGateway,
        refresh_token_gateway: RefreshTokenGateway,
        commiter: ICommitter,
        jwt_service: JwtService
    ) -> None:
        self.user_gateway = user_gateway
        self.refresh_token_gateway = refresh_token_gateway
        self.commiter = commiter
        self.jwt_service = jwt_service

    
    async def __call__(self, refresh_token: RefreshTokenDTO) -> tuple[RefreshTokenDTO, AccessTokenDTO]:
        
        user = await self.user_gateway.get(refresh_token.user_ident)

        if not user:
            raise UserNotFound(refresh_token.user_ident)
        

        if refresh_token.revoked:
            await self.refresh_token_gateway.revoke_all_user_tokens(user.ident)

            raise RefreshTokenRevoked

        refresh_token = gen_new_refresh_token(user, self.jwt_service)
        access_token = gen_new_access_token(user, self.jwt_service)

        await self.refresh_token_gateway.insert(convert_refresh_token_dto_to_create_refresh_token_dto(refresh_token))

        await self.commiter.commit()

        return (refresh_token, access_token)


class LogoutUserInteractor:
    def __init__(
        self,
        refresh_token_gateway: RefreshTokenGateway,
        commiter: ICommitter
    ) -> None:
        self.refresh_token_gateway = refresh_token_gateway
        self.commiter = commiter

    
    async def __call__(self, refresh_token: RefreshTokenDTO):
        await self.refresh_token_gateway.revoke_all_user_tokens(refresh_token.user_ident)

        await self.commiter.commit()


class ValidateAccessInteractor:
    
    async def __call__(self, access_token: AccessTokenDTO):

        if access_token.expired:
            raise AccessTokenExpired
