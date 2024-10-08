from uuid import UUID

from naks_library.testing.base_test_db_service import BaseTestDBService
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
import pytest

from services.db_services import *
from src.utils.DTOs import *
from database import engine
from shemas import *
from funcs import test_data


@pytest.mark.asyncio
class TestUserDBService(BaseTestDBService):
    service: UserDBService = UserDBService()
    session = AsyncSession(engine)
    __dto__ = UserData
    __create_shema__ = CreateUserShema
    __update_shema__ = UpdateUserShema


    @pytest.mark.usefixtures("users_dicts")
    async def test_insert(self, users_dicts: list[dict]) -> None:
        await super().test_insert(users_dicts)


    @pytest.mark.usefixtures('users')
    @pytest.mark.parametrize(
        "index",
        [0, 5, 7, 9]
    )
    async def test_get(self, users: list[UserData], index: int) -> None:
        user = users[index]

        await super().test_get(user.ident, user)


    @pytest.mark.usefixtures('users')
    @pytest.mark.parametrize(
        "index",
        [1, 8, 6, 4]
    )
    async def test_get_by_login(self, users: list[UserData], index: int) -> None:
        user = users[index]

        assert await self.service.get_by_login(self.session, user.login) == user


    @pytest.mark.parametrize(
        "ident, data",
        [(user.ident, new_user_data) for user, new_user_data in zip(test_data.fake_users[:5], test_data.fake_user_generator.generate(5))]
    )
    async def test_update(self, ident: str, data: dict) -> None: 
        await super().test_update(ident, data)


    @pytest.mark.usefixtures('users_dicts')
    @pytest.mark.parametrize(
            "index",
            [0, 5, 9]
    )
    async def test_delete(self, users_dicts: list[dict], index: int) -> None:
        user = users_dicts[index]

        await super().test_delete(user["ident"], user)


@pytest.mark.asyncio
class TestRefreshTokenDBService(BaseTestDBService): 
    service = RefreshTokenDBService()
    session = AsyncSession(engine)
    __dto__ = RefreshTokenData
    __create_shema__ = CreateRefreshTokenShema
    __update_shema__ = UpdateRefreshTokenShema


    @pytest.mark.usefixtures("refresh_tokens_dicts")
    async def test_insert(self, refresh_tokens_dicts: list[dict]) -> None:
        await super().test_insert(refresh_tokens_dicts)


    @pytest.mark.usefixtures('refresh_tokens')
    @pytest.mark.parametrize(
            "index",
            [1, 2, 4]
    )
    async def test_get(self, refresh_tokens: list[RefreshTokenData], index: int) -> None:
        refresh_token = refresh_tokens[index]

        await super().test_get(refresh_token.ident, refresh_token)


    @pytest.mark.parametrize(
        "ident, data",
        [(refresh_token.ident, new_refresh_token_data) for refresh_token, new_refresh_token_data in zip(test_data.fake_refresh_tokens[:5], test_data.fake_refresh_token_generator.generate(5))]
    )
    async def test_update(self, ident: str, data: dict) -> None:
        await super().test_update(ident, data)


    @pytest.mark.usefixtures('refresh_tokens_dicts')
    @pytest.mark.parametrize(
        "index",
        [1, 2, 4]
    )
    async def test_delete(self, refresh_tokens_dicts: list[dict], index: int) -> None:
        refresh_token = refresh_tokens_dicts[index]

        await super().test_delete(refresh_token["ident"], refresh_token)
