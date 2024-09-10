from uuid import UUID

from naks_library import BaseDBService, BaseShema, to_uuid
from naks_library.utils import *
from sqlalchemy import update, and_, join, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute

from src.utils.DTOs import *
from src.models import *
from src.shemas import *


__all__: list[str] = [
    "UserDBService",
    "RefreshTokenDBService"
]


USER_FILTERS_MAP: dict[str, AbstractFilter] = {}


USER_SELECT_ATTRS = [
]


USER_SELECT_FROM_ATTRS = [
]


USER_OR_SELECT_COLUMNS: list[InstrumentedAttribute] = [
]


USER_AND_SELECT_COLUMNS: list[InstrumentedAttribute] = [
]


type UserSelectShema = BaseShema


class UserDBService(BaseDBService[UserData, UserModel, UserSelectShema, CreateUserShema, UpdateUserShema]):
    __dto__ = UserData
    __model__ = UserModel
    _filters_map = USER_FILTERS_MAP
    _select_attrs = USER_SELECT_ATTRS
    _select_from_attrs = USER_SELECT_FROM_ATTRS
    _and_model_columns = USER_AND_SELECT_COLUMNS
    _or_model_columns = USER_OR_SELECT_COLUMNS

    async def get_by_login(self, session: AsyncSession, login: str) -> UserData | None:

        async with session as session:
            stmt = select(self.__model__).where(
                self.__model__.login == login
            )

            res = (await session.execute(stmt)).scalar_one_or_none()
 
            if res:
                return self.__dto__(**res.__dict__)


REFRESH_TOKEN_FILTERS_MAP: dict[str, AbstractFilter] = {
    "tokens": InFilter(RefreshTokenModel.token),
    "idents": InFilter(RefreshTokenModel.ident),
    "user_idents": InFilter(UserModel.ident),
    "revoked": EqualFilter(RefreshTokenModel.revoked),
    "gen_dt_from": FromFilter(RefreshTokenModel.gen_dt),
    "gen_dt_before": BeforeFilter(RefreshTokenModel.gen_dt),
    "exp_dt_from": FromFilter(RefreshTokenModel.exp_dt),
    "exp_dt_before": BeforeFilter(RefreshTokenModel.exp_dt),
}


REFRESH_TOKEN_SELECT_ATTRS = [
    RefreshTokenModel
]


REFRESH_TOKEN_SELECT_FROM_ATTRS = [
    join(RefreshTokenModel, UserModel)
]


REFRESH_TOKEN_OR_SELECT_COLUMNS: list[InstrumentedAttribute] = [
    RefreshTokenModel.token,
    RefreshTokenModel.ident,
    UserModel.ident
]


REFRESH_TOKEN_AND_SELECT_COLUMNS: list[InstrumentedAttribute] = [
    RefreshTokenModel.revoked,
    RefreshTokenModel.gen_dt,
    RefreshTokenModel.exp_dt
]


class RefreshTokenDBService(BaseDBService[RefreshTokenData, RefreshTokenModel, RefreshTokenSelectShema, CreateRefreshTokenShema, UpdateRefreshTokenShema]):
    __dto__ = RefreshTokenData
    __model__ = RefreshTokenModel
    _filters_map = REFRESH_TOKEN_FILTERS_MAP
    _select_attrs = REFRESH_TOKEN_SELECT_ATTRS
    _select_from_attrs = REFRESH_TOKEN_SELECT_FROM_ATTRS
    _and_model_columns = REFRESH_TOKEN_AND_SELECT_COLUMNS
    _or_model_columns = REFRESH_TOKEN_OR_SELECT_COLUMNS


    async def get_by_token(self, session: AsyncSession, token: str) -> RefreshTokenData | None:

        async with session as session:
            stmt = select(self.__model__).where(
                self.__model__.token == token
            )

            res = (await session.execute(stmt)).scalar_one_or_none()
 
            if res:
                return self.__dto__(**res.__dict__)


    async def revoke_all_user_tokens(self, session: AsyncSession, user_ident: str | UUID) -> None:
        user_ident = to_uuid(user_ident)
 
        async with session as session:
            stmt = update(self.__model__).where(
                and_(
                    self.__model__.user_ident == user_ident,
                    self.__model__.revoked == False
                )
            ).values(
                revoked=True
            )

            await session.execute(stmt)
            await session.commit()
