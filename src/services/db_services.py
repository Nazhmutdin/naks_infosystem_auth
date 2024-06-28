from uuid import UUID

from naks_library import BaseRequestShema, to_uuid
from naks_library import BaseDBService
from sqlalchemy import update, and_

from src.models import *
from src.shemas import *


__all__: list[str] = [
    "UserDBService",
    "RefreshTokenDBService"
]


class UserDBService(BaseDBService[UserShema, UserModel, BaseRequestShema]):
    __shema__ = UserShema
    __model__ = UserModel


class RefreshTokenDBService(BaseDBService[RefreshTokenShema, RefreshTokenModel, RefreshTokenRequestShema]):
    __shema__ = RefreshTokenShema
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
