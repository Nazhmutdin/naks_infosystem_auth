from uuid import UUID

from naks_library.crud_mapper import SqlAlchemyCrudMapper
from sqlalchemy import update, select

from app.application.dto import (
    UserDTO, 
    CreateUserDTO, 
    UpdateUserDTO,
    RefreshTokenDTO,
    CreateRefreshTokenDTO,
    UpdateRefreshTokenDTO,
    PermissionDTO,
    CreatePermissionDTO,
    UpdatePermissionDTO
)
from app.infrastructure.database.models import UserModel, RefreshTokenModel, PermissionModel


class UserMapper(SqlAlchemyCrudMapper[UserDTO, CreateUserDTO, UpdateUserDTO]):
    __model__ = UserModel

    async def get_by_login(self, login: str) -> UserDTO | None:
        stmt = select(UserModel).where(
            UserModel.login == login
        )

        res = (await self.session.execute(stmt)).scalars().one_or_none()

        if res:
            return self._convert(res)


    def _convert(self, row: UserModel) -> UserDTO:
        return UserDTO(
            ident=row.ident,
            login=row.login,
            name=row.name,
            email=row.email,
            hashed_password=row.hashed_password,
            sign_dt=row.sign_dt,
            update_dt=row.update_dt,
            login_dt=row.login_dt
        )


class RefreshTokenMapper(SqlAlchemyCrudMapper[RefreshTokenDTO, CreateRefreshTokenDTO, UpdateRefreshTokenDTO]):
    __model__ = RefreshTokenModel


    async def revoke_all_user_tokens(self, ident: UUID):
        stmt = update(RefreshTokenModel).where(
            RefreshTokenModel.user_ident == ident
        ).values(
            revoked=True
        )

        await self.session.execute(stmt)


    def _convert(self, row: RefreshTokenModel) -> RefreshTokenDTO:
        return RefreshTokenDTO(**row.__dict__)


class PermissionMapper(SqlAlchemyCrudMapper[PermissionDTO, CreatePermissionDTO, UpdatePermissionDTO]):
    __model__ = PermissionModel


    async def get_by_user_ident(self, user_ident: UUID) -> PermissionDTO | None:
        stmt = select(PermissionModel).where(
            PermissionModel.user_ident == user_ident
        )
        res = (await self.session.execute(stmt)).scalars().one_or_none()

        if res:
            return self._convert(res)


    def _convert(self, row: PermissionModel) -> PermissionDTO:
        return PermissionDTO(**row.__dict__)
