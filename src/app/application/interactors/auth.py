from uuid import uuid4
from datetime import timedelta, datetime

from naks_library.interfaces import ICommitter
from fastapi import Request

from app.application.interfaces.gateways import UserGateway, RefreshTokenGateway, PermissionGateway
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


class ValidateDataAccessInteractor:

    def __init__(
            self,
            permission_gateway: PermissionGateway
    ):
        self.permission_gateway = permission_gateway
    

    async def __call__(self, access_token: AccessTokenDTO, request: Request):
        original_method = request.headers.get("x-original-method")
        original_uri = request.headers.get("x-original-uri")

        permissions = await self.permission_gateway.get_by_user_ident(access_token.user_ident)
    
        if not permissions:
            raise PermissionDataNotFound(user_ident=access_token.user_ident)


        if permissions.is_super_user:
            return


        if not original_method:
            raise OriginalMethodNotFound


        if not original_uri:
            raise OriginalUriNotFound


        if access_token.expired:
            raise AccessTokenExpired


        if not self.is_permitted(
            uri=original_uri,
            method=original_method,
            permissions=permissions
        ):
            raise AccessForbidden


    def is_permitted(self, uri: str, method: str, permissions: PermissionDTO) -> bool:

        if "v1/personal-naks-certification" in uri:
            return self._get_permission("personal_naks_certification_data", method, permissions)

        elif "v1/personal" in uri:
            return self._get_permission("personal_data", method, permissions)

        elif "v1/ndt" in uri:
            return self._get_permission("ndt_data", method, permissions)

        elif "v1/acst" in uri:
            return self._get_permission("acst_data", method, permissions)


    def _get_permission(self, start_with: str, method: str, permissions: PermissionDTO) -> bool:
        if method == "GET":
            method = "get"
        elif method == "POST":
            method = "create"
        elif method == "PATCH":
            method = "update"
        elif method == "DELETE":
            method = "delete"
   
        res = permissions.__dict__.get(f"{start_with}_{method}")

        return res


class ValidateFileAccessInteractor:

    def __init__(
            self,
            permission_gateway: PermissionGateway
    ):
        self.permission_gateway = permission_gateway
    

    async def __call__(self, access_token: AccessTokenDTO, request: Request):
        original_method = request.headers.get("x-original-method")
        original_uri = request.headers.get("x-original-uri")

        permissions = await self.permission_gateway.get_by_user_ident(access_token.user_ident)
    
        if not permissions:
            raise PermissionDataNotFound(user_ident=access_token.user_ident)


        if permissions.is_super_user:
            return


        if not original_method:
            raise OriginalMethodNotFound


        if not original_uri:
            raise OriginalUriNotFound


        if access_token.expired:
            raise AccessTokenExpired


        if not self.is_permitted(
            uri=original_uri,
            method=original_method,
            permissions=permissions
        ):
            raise AccessForbidden


    def is_permitted(self, uri: str, method: str, permissions: PermissionDTO) -> bool:

        raise NotImplementedError


    def _get_permission(self, start_with: str, method: str, permissions: PermissionDTO) -> bool: ...



class ValidateSuperUserAccessInteractor:

    def __init__(
            self,
            permission_gateway: PermissionGateway
    ):
        self.permission_gateway = permission_gateway
    

    async def __call__(self, access_token: AccessTokenDTO):

        permissions = await self.permission_gateway.get_by_user_ident(access_token.user_ident)
    
        if not permissions:
            raise PermissionDataNotFound(user_ident=access_token.user_ident)


        if not permissions.is_super_user:
            raise AccessForbidden
