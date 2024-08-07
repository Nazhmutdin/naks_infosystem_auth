from sqlalchemy.ext.asyncio import AsyncSession
from naks_library.testing.base_test_model import BaseTestModel
import pytest

from src.utils.DTOs import UserData, RefreshTokenData
from src.utils.uows import UOW
from src.database import engine
from funcs import test_data
from src.models import *

"""
===================================================================================================================
User repository test
===================================================================================================================
"""


@pytest.mark.asyncio
class TestUserModel(BaseTestModel[UserData]):
    __model__ = UserModel
    __dto__ = UserData

    
    uow = UOW(AsyncSession(engine))


    @pytest.mark.usefixtures('users')
    async def test_create(self, users: list[UserData]) -> None:
        await super().test_create(users)


    @pytest.mark.usefixtures('users')
    @pytest.mark.parametrize(
        "index",
        [1, 2, 7]
    )
    async def test_create_existing(self, users: list[UserData], index: int) -> None:
        await super().test_create_existing(users[index])


    @pytest.mark.usefixtures('users')
    @pytest.mark.parametrize(
        "index, attr",
        [
            (1, "login"),
            (3, "ident"),
            (7, "login"),
            (5, "ident")
        ]
    )
    async def test_get(self, users: list[UserData], index: int, attr: str) -> None:
        ident = getattr(users[index], attr)

        await super().test_get(ident, users[index])


    @pytest.mark.parametrize(
        "ident, data",
        [(user.ident, new_user_data) for user, new_user_data in zip(test_data.fake_users[:5], test_data.fake_user_generator.generate(5))]
    )
    async def test_update(self, ident: str, data: dict) -> None:
        await super().test_update(ident, data)


    @pytest.mark.usefixtures('users')
    @pytest.mark.parametrize(
            "index",
            [0, 5, 9]
    )
    async def test_delete(self, users: list[UserData], index: int) -> None:
        ident = getattr(users[index], "ident")

        await super().test_delete(ident, users[index])


"""
===================================================================================================================
refresh token repository test
===================================================================================================================
"""


@pytest.mark.asyncio
class TestRefreshTokenModel(BaseTestModel[RefreshTokenData]): 
    __model__ = RefreshTokenModel
    __dto__ = RefreshTokenData

    uow = UOW(AsyncSession(engine))


    @pytest.mark.usefixtures("refresh_tokens")
    async def test_create(self, refresh_tokens: list[RefreshTokenData]) -> None:
        await super().test_create(refresh_tokens)


    @pytest.mark.usefixtures('refresh_tokens')
    @pytest.mark.parametrize(
            "index",
            [1, 2, 4]
    )
    async def test_create_existing(self, refresh_tokens: list[RefreshTokenData], index: int) -> None: 
        await super().test_create_existing(refresh_tokens[index])


    @pytest.mark.usefixtures('refresh_tokens')
    @pytest.mark.parametrize(
            "index",
            [1, 2, 4]
    )
    async def test_get(self, refresh_tokens: list[RefreshTokenData], index: int) -> None:
        ident = getattr(refresh_tokens[index], "ident")

        await super().test_get(ident, refresh_tokens[index])


    @pytest.mark.parametrize(
        "ident, data",
        [(refresh_token.ident, new_refresh_token_data) for refresh_token, new_refresh_token_data in zip(test_data.fake_refresh_tokens[:5], test_data.fake_refresh_token_generator.generate(5))]
    )
    async def test_update(self, ident: str, data: dict) -> None:
        await super().test_update(ident, data)


    @pytest.mark.usefixtures('refresh_tokens')
    @pytest.mark.parametrize(
            "index",
            [1, 2, 4]
    )
    async def test_delete(self, refresh_tokens: list[RefreshTokenData], index: int) -> None:
        ident = getattr(refresh_tokens[index], "ident")

        await super().test_delete(ident, refresh_tokens[index])
