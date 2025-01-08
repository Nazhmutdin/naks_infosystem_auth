import typing as t
from uuid import UUID, uuid4
from datetime import timedelta, datetime

from naks_library.interfaces import ICommitter
from fastapi import Request

from app.application.interfaces.gateways import UserGateway, RefreshTokenGateway, PermissionGateway, RedisGateway
from app.application.common.exc import (
    UserNotFound, 
    InvalidPassword, 
    RefreshTokenRevoked,
    AccessTokenExpired, 
    OriginalMethodNotFound, 
    OriginalUriNotFound,
    PermissionDataNotFound,
    AccessForbidden
)
from app.application.dto import UserDTO, RefreshTokenDTO, PermissionDTO, convert_refresh_token_dto_to_create_refresh_token_dto
from app.infrastructure.dto import AccessTokenDTO, LoginData
from app.infrastructure.services.jwt_service import JwtService
from app.infrastructure.services.hasher import PasswordHasher
from app.config import ApplicationConfig


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
            raise UserNotFound(
                data.login
            )

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

    def __init__(
            self,
            user_gateway: UserGateway,
            permission_gateway: PermissionGateway,
            redis_gateway: RedisGateway
    ):
        self.user_gateway = user_gateway
        self.permission_gateway = permission_gateway
        self.redis_gateway = redis_gateway

        self.func_map: dict[t.Callable[[PermissionDTO], None]]={
            "GET-/v1/user": "is_super_user",
            "PATCH-/v1/user": "is_super_user",
            "POST-/v1/user": "is_super_user",
            "DELETE-/v1/user": "is_super_user",

            "GET-/v1/personal": "personal_data_get",
            "GET-/v1/personal/select": "personal_data_get",
            "PATCH-/v1/personal": "personal_data_update",
            "POST-/v1/personal": "personal_data_create",
            "DELETE-/v1/personal": "personal_data_delete",

            "GET-/v1/ndt": "ndt_data_get",
            "GET-/v1/ndt/select": "ndt_data_get",
            "GET-/v1/ndt/personal": "ndt_data_get",
            "PATCH-/v1/ndt": "ndt_data_update",
            "POST-/v1/ndt": "ndt_data_create",
            "DELETE-/v1/ndt": "ndt_data_delete",

            "GET-/v1/personal-naks-certification": "personal_naks_certification_data_get",
            "GET-/v1/personal-naks-certification/select": "personal_naks_certification_data_get",
            "GET-/v1/personal-naks-certification/personal": "personal_naks_certification_data_get",
            "PATCH-/v1/personal-naks-certification": "personal_naks_certification_data_update",
            "POST-/v1/personal-naks-certification": "personal_naks_certification_data_create",
            "DELETE-/v1/personal-naks-certification": "personal_naks_certification_data_delete",

            "GET-/v1/acst": "acst_data_get",
            "GET-/v1/acst/select": "acst_data_get",
            "PATCH-/v1/acst": "acst_data_update",
            "POST-/v1/acst": "acst_data_create",
            "DELETE-/v1/acst": "acst_data_delete"
        }

    
    async def __call__(self, access_token: AccessTokenDTO, request: Request) -> tuple[UserDTO, PermissionDTO]:
            
        if access_token.expired:
            raise AccessTokenExpired
        
        user = await self._get_user(access_token.user_ident)
        permissions = await self._get_permissions(access_token.user_ident)

        if not permissions:
            raise PermissionDataNotFound(user_ident=access_token.user_ident)

        if not user:
            raise UserNotFound(ident=access_token.user_ident)
    

        await self.redis_gateway.set_permission(access_token.user_ident, permissions)
        await self.redis_gateway.set_user(access_token.user_ident, user)


        if permissions.is_super_user:
            return user, permissions

        
        original_method = request.headers.get("x-original-method")
        original_uri = request.headers.get("x-original-uri").split("?")[0]


        if not original_method:
            raise OriginalMethodNotFound


        if not original_uri:
            raise OriginalUriNotFound
        
        
        access_key: str | None = self.func_map.get(f"{original_method}-{original_uri}", None)

        if not getattr(permissions, access_key):
            raise AccessForbidden()

        return user, permissions
    

    async def _get_user(self, user_ident: UUID) -> UserDTO | None:

        user = await self.redis_gateway.get_user(user_ident)

        if not user:
            user = await self.user_gateway.get(user_ident)
    
        return user
    

    async def _get_permissions(self, user_ident: UUID) -> PermissionDTO | None:

        permissions = await self.redis_gateway.get_permission(user_ident)

        if not permissions:
            permissions = await self.permission_gateway.get_by_user_ident(user_ident)
    
        return permissions

