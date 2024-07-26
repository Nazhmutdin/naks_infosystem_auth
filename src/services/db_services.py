from uuid import UUID

from naks_library import BaseRequestShema, to_uuid
from naks_library import BaseDBService
from sqlalchemy import update, and_

from src.utils.DTOs import *
from src.models import *
from src.shemas import *


__all__: list[str] = [
    "UserDBService",
    "RefreshTokenDBService"
]


class UserDBService(BaseDBService[UserData, UserModel, BaseRequestShema, CreateUserShema, UpdateUserShema]):
    __dto__ = UserData
    __model__ = UserModel


class RefreshTokenDBService(BaseDBService[RefreshTokenData, RefreshTokenModel, RefreshTokenRequestShema, CreateRefreshTokenShema, UpdateRefreshTokenShema]):
    __dto__ = RefreshTokenData
    __model__ = RefreshTokenModel

    async def revoke_all_user_tokens(self, user_ident: str | UUID) -> None:
        user_ident = to_uuid(user_ident)
 
        async with self.uow as uow:
            stmt = update(self.__model__).where(
                and_(
                    self.__model__.user_ident == user_ident,
                    self.__model__.revoked == False
                )
            ).values(
                revoked=True
            )

            await uow.conn.execute(stmt)
            await uow.commit()
