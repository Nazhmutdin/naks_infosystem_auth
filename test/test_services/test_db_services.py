from uuid import UUID

from naks_library.testing.base_test_db_service import BaseTestDBService
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
import pytest

from services.db_services import *
from database import engine
from shemas import *


@pytest.mark.asyncio
class TestUserDBService(BaseTestDBService[UserShema]):
    service = UserDBService(AsyncSession(engine))
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
            ("TestUser", {"name": "UpdatedName", "email": "hello@mail.ru"}),
            ("eee02230b2f34440bb349480a809bb10", {"sign_dt": "2024-01-17T13:38:12.906854", "is_superuser": False}),
            ("TestUser6", {"login_dt": "2024-07-19T13:38:45.906854"}),
        ]
    )
    async def test_update(self, ident: str, data: dict) -> None: 
        await super().test_update(ident, data)


    @pytest.mark.parametrize(
        "ident, data, exception",
        [
            ("TestUser", {"name": "UpdatedName", "email": "@mail.ru"}, ValidationError),
            ("eee02230b2f34440bb349480a809bb10", {"sign_dt": "2024-11-17T13:38:12.906854", "is_superuser": "ggg"}, ValidationError),
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
class TestRefreshTokenDBService(BaseTestDBService[RefreshTokenShema]): 
    service = RefreshTokenDBService(AsyncSession(engine))
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
            ("01167611c3964222ae5263363c3b33f6", {"revoked": True}),
            ("c4b256677aac45a994ef5ee414f44772", {"user_ident": UUID("72e38f60a025499db25c74aac04ca19b")}),
            ("5f741f170c8045648e769e4fd63dba7e", {"exp_dt": "2024-06-01T13:38:12"}),
        ]
    )
    async def test_update(self, ident: str, data: dict) -> None:
        await super().test_update(ident, data)


    @pytest.mark.parametrize(
        "ident, data, exception",
        [
            ("7b0d0e8a4f214fbbafd6f4a6f5cdd9e3", {"revoked": "hello"}, ValidationError),
            ("c4b256677aac45a994ef5ee414f44772", {"user_ident": "72e38f60a024495c7c04ca19b"}, ValidationError),
            ("f7e416d52ad542f38fb0e3947f673119", {"exp_dt": "ggg"}, ValidationError),
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
