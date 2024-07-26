from uuid import UUID

from naks_library.testing.base_test_db_service import BaseTestDBService
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
import pytest

from services.db_services import *
from src.utils.DTOs import *
from database import engine
from shemas import *


@pytest.mark.asyncio
class TestUserDBService(BaseTestDBService):
    service = UserDBService(AsyncSession(engine))
    __dto__ = UserData
    __create_shema__ = CreateUserShema
    __update_shema__ = UpdateUserShema


    @pytest.mark.usefixtures('users')
    async def test_add(self, users: list[UserShema]) -> None:
        await super().test_add(users)


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
    async def test_get(self, users: list[UserShema], index: int, attr: str) -> None:
        await super().test_get(attr, users[index])


    @pytest.mark.parametrize(
        "ident, data",
        [
            ("TestUser1", {"name": "UpdatedName", "email": "hello@mail.ru"}),
            ("755d4fe7e8984fb997ef3de62ebf9313", {"sign_dt": "2024-01-17T13:38:12.906854", "is_superuser": False}),
            ("TestUser6", {"login_dt": "2024-07-19T13:38:45.906854"}),
        ]
    )
    async def test_update(self, ident: str, data: dict) -> None: 
        await super().test_update(ident, data)


    @pytest.mark.parametrize(
        "ident, data, exception",
        [
            ("TestUser1", {"name": "UpdatedName", "email": "@mail.ru"}, ValidationError),
            ("755d4fe7e8984fb997ef3de62ebf9313", {"sign_dt": "2024-11-17T13:38:12.906854", "is_superuser": "ggg"}, ValidationError),
            ("TestUser6", {"login_dt": "2024-17-19T13:38:45.906854"}, ValidationError),
        ]
    )
    async def test_fail_update(self, ident: str, data: dict, exception) -> None:
        await super().test_fail_update(ident, data, exception)


    @pytest.mark.usefixtures('users')
    @pytest.mark.parametrize(
            "index",
            [0, 5, 9]
    )
    async def test_delete(self, users: list[UserShema], index: int) -> None:
        await super().test_delete(users[index])


@pytest.mark.asyncio
class TestRefreshTokenDBService(BaseTestDBService): 
    service = RefreshTokenDBService(AsyncSession(engine))
    __dto__ = RefreshTokenData
    __create_shema__ = CreateRefreshTokenShema
    __update_shema__ = UpdateRefreshTokenShema


    @pytest.mark.usefixtures("refresh_tokens")
    async def test_add(self, refresh_tokens: list[RefreshTokenShema]) -> None:
        await super().test_add(refresh_tokens)


    @pytest.mark.usefixtures('refresh_tokens')
    @pytest.mark.parametrize(
            "index",
            [1, 2, 4]
    )
    async def test_get(self, refresh_tokens: list[RefreshTokenShema], index: int) -> None:
        await super().test_get("ident", refresh_tokens[index])


    @pytest.mark.parametrize(
        "ident, data",
        [
            ("543417b0599140b1ab979798cce171e0", {"revoked": True}),
            ("15910d47da2d425282c2b2d749124cd3", {"user_ident": UUID("b7416aebf670413fb848ce173bbe2ab0")}),
            ("0a96a91daae641d4aa783a9fff6b2ce6", {"exp_dt": "2024-06-01T13:38:12"}),
        ]
    )
    async def test_update(self, ident: str, data: dict) -> None:
        await super().test_update(ident, data)


    @pytest.mark.parametrize(
        "ident, data, exception",
        [
            ("0a96a91daae641d4aa783a9fff6b2ce6", {"revoked": "hello"}, ValidationError),
            ("b370730c403243d684418e8e6f5a6ce4", {"user_ident": "72e38f60a024495c7c04ca19b"}, ValidationError),
            ("60224ef230134811a9953d0515d6e4f4", {"exp_dt": "ggg"}, ValidationError),
        ]
    )
    async def test_fail_update(self, ident: str, data: dict, exception) -> None:
        await super().test_fail_update(ident, data, exception)


    @pytest.mark.usefixtures('refresh_tokens')
    @pytest.mark.parametrize(
            "index",
            [1, 2, 4]
    )
    async def test_delete(self, refresh_tokens: list[RefreshTokenShema], index: int) -> None:
        await super().test_delete(refresh_tokens[index])
