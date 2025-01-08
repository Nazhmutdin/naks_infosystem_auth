from uuid import UUID
from typing import Protocol

from naks_library.interfaces import ICrudGateway

from app.application.dto import (
    UserDTO,
    CreateUserDTO,
    RefreshTokenDTO,
    CreateRefreshTokenDTO, 
    PermissionDTO,
    CreatePermissionDTO
)

from redis.asyncio import Redis


class RedisGateway(Protocol): 

    def __init__(self, redis_engine: Redis): ...


    async def get_user(
        self,
        ident: UUID
    ) -> UserDTO | None: ...


    async def set_user(
        self,
        ident: UUID,
        data: UserDTO
    ) -> None: ...


    async def delete_user(
        self,
        ident: UUID
    ) -> None: ...


    async def get_permission(
        self,
        ident: UUID
    ) -> PermissionDTO | None: ...


    async def set_permission(
        self,
        ident: UUID,
        data: PermissionDTO
    ) -> None: ...


    async def delete_permission(
        self,
        ident: UUID
    ) -> None: ...


    async def get_refresh_token(
        self,
        ident: UUID
    ) -> PermissionDTO | None: ...


    async def set_refresh_token(
        self,
        ident: UUID,
        data: PermissionDTO
    ) -> None: ...


    async def delete_refresh_token(
        self,
        ident: UUID
    ) -> None: ...


class UserGateway(ICrudGateway[UserDTO, CreateUserDTO]):
    async def get_by_login(self, login: str) -> UserDTO | None: ...


class RefreshTokenGateway(ICrudGateway[RefreshTokenDTO, CreateRefreshTokenDTO]): 
    async def revoke_all_user_tokens(self, ident: UUID): ...


class PermissionGateway(ICrudGateway[PermissionDTO, CreatePermissionDTO]): 
    async def get_by_user_ident(self, user_ident: UUID) -> PermissionDTO | None: ...
