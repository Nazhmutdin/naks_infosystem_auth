from uuid import UUID

from redis.asyncio import Redis
from pydantic import RootModel

from app.application.dto import UserDTO, PermissionDTO, RefreshTokenDTO
from app.config import RedisConfig


class RedisMapper:

    def __init__(self, redis_engine: Redis):
        self.redis_engine = redis_engine


    async def get_user(
        self,
        ident: UUID
    ) -> UserDTO | None:
        res = await self._get(f"user:{ident.hex}")

        if res:
            return RootModel[UserDTO].model_validate_json(res).root


    async def set_user(
        self,
        ident: UUID,
        data: UserDTO
    ) -> None:

        await self._set(
            f"user:{ident.hex}", 
            RootModel[UserDTO](data).model_dump_json()
        )


    async def delete_user(
        self,
        ident: UUID
    ) -> None:
        await self._delete(f"user:{ident.hex}")


    async def get_permission(
        self,
        ident: UUID
    ) -> PermissionDTO | None:
        res = await self._get(f"permission:{ident.hex}")

        if res:
            return RootModel[PermissionDTO].model_validate_json(res).root


    async def set_permission(
        self,
        ident: UUID,
        data: PermissionDTO
    ) -> None:

        await self._set(
            f"permission:{ident.hex}", 
            RootModel[PermissionDTO](data).model_dump_json()
        )


    async def delete_permission(
        self,
        ident: UUID
    ) -> None:
        await self._delete(f"permission:{ident.hex}")


    async def get_refresh_token(
        self,
        ident: UUID
    ) -> PermissionDTO | None:
        res = await self._get(f"refresh-token:{ident.hex}")

        if res:
            return RootModel[RefreshTokenDTO].model_validate_json(res).root


    async def set_refresh_token(
        self,
        ident: UUID,
        data: PermissionDTO
    ) -> None:

        await self._set(
            f"refresh-token:{ident.hex}", 
            RootModel[RefreshTokenDTO](data).model_dump_json()
        )


    async def delete_refresh_token(
        self,
        ident: UUID
    ) -> None:
        await self._delete(f"refresh-token:{ident.hex}")


    async def _get(
        self,
        key: str
    ) -> str | None:
        return await self.redis_engine.get(key)


    async def _set(
        self,
        key: str,
        data: str
    ) -> None:
        await self.redis_engine.set(key, data, RedisConfig.CACHE_EXP())


    async def _delete(
        self,
        key: str
    ) -> None:
        await self.redis_engine.delete(key)
