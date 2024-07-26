from datetime import date, datetime
from uuid import UUID
import typing as t

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from naks_library import BaseShema, BaseRequestShema, to_date
import pytest

from src.utils.uows import UOW
from src.database import engine
from src.shemas import *
from src.models import *


"""
===================================================================================================================
repository base test
===================================================================================================================
"""


@pytest.mark.usefixtures("prepare_db")
class BaseTestModel[Shema: BaseShema]:
    __shema__: type[BaseShema]
    __model__: type[Base]

    uow = UOW(AsyncSession(engine))

    async def test_create(self, data: list[Shema]) -> None:
        async with self.uow as uow:

            insert_data = [
                el.__dict__ for el in data
            ]
            
            await self.__model__.create(
                insert_data,
                conn=uow.session
            )

            for el in data:
                el = self.__shema__.model_validate(el, from_attributes=True)
                res = await self.__model__.get(uow.session, el.ident)
                result = self.__shema__.model_validate(res, from_attributes=True)
                assert result == el

            assert await self.__model__.count(uow.session) == len(data)

            await uow.commit()


    async def test_create_existing(self, data: Shema) -> None:

        async with self.uow as uow:

            with pytest.raises(IntegrityError):
                await self.__model__.create(
                    data.model_dump(),
                    conn=uow.session
                )

            await uow.commit()


    async def test_get(self, attr: str, el: Shema) -> None:

        async with self.uow as uow:
            res = await self.__model__.get(uow.session, getattr(el, attr))

            assert self.__shema__.model_validate(res, from_attributes=True) == el

    
    async def test_get_many(self, k: int, request_shema: BaseRequestShema) -> None:

        async with self.uow as uow:

            res = await self.__model__.get_many(
                uow.session,
                request_shema.dump_expression(),
                limit=request_shema.limit,
                offset=request_shema.offset
            )

            assert len(res[0]) == k


    async def test_update(self, ident: str, data: dict[str, t.Any]) -> None:
        async with self.uow as uow:

            await self.__model__.update(uow.session, ident, data)

            res = await self.__model__.get(uow.session, ident)

            el = self.__shema__.model_validate(res, from_attributes=True)

            for key, value in data.items():
                if isinstance(getattr(el, key), date):
                    assert getattr(el, key) == to_date(value, False)
                    continue

                assert getattr(el, key) == value

            await uow.commit()


    async def test_delete(self, item: Shema) -> None:
        async with self.uow as uow:

            await self.__model__.delete(uow.session, item.ident)

            assert not await self.__model__.get(uow.session, item.ident)

            await self.__model__.create(item.model_dump(), conn=uow.session)

            await uow.commit()


"""
===================================================================================================================
User repository test
===================================================================================================================
"""


@pytest.mark.asyncio
class TestUserModel(BaseTestModel[UserShema]):
    __shema__ = UserShema
    __model__ = UserModel


    @pytest.mark.usefixtures('users')
    async def test_create(self, users: list[UserShema]) -> None:
        await super().test_create(users)


    @pytest.mark.usefixtures('users')
    @pytest.mark.parametrize(
        "index",
        [1, 2, 7]
    )
    async def test_create_existing(self, users: list[UserShema], index: int) -> None:
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
    async def test_get(self, users: list[UserShema], index: int, attr: str) -> None:
        await super().test_get(attr, users[index])

        
    async def test_get_many(self) -> None: ...


    @pytest.mark.parametrize(
        "ident, data",
        [
            ("TestUser1", {"name": "UpdatedName", "email": "hello@mail.ru"}),
            ("755d4fe7-e898-4fb9-97ef-3de62ebf9313", {"sign_dt": datetime(2024, 1, 11, 8, 38, 12, 906854), "is_superuser": False}),
            ("TestUser6", {"login_dt": datetime(2024, 1, 1, 8, 38, 12, 906854)}),
        ]
    )
    async def test_update(self, ident: str, data: dict) -> None:
        await super().test_update(ident, data)


    @pytest.mark.usefixtures('users')
    @pytest.mark.parametrize(
            "index",
            [0, 5, 9]
    )
    async def test_delete(self, users: list[UserShema], index: int) -> None:
        await super().test_delete(users[index])


"""
===================================================================================================================
refresh token repository test
===================================================================================================================
"""


@pytest.mark.asyncio
class TestRefreshTokenModel(BaseTestModel[RefreshTokenShema]): 
    __shema__ = RefreshTokenShema
    __model__ = RefreshTokenModel


    @pytest.mark.usefixtures("refresh_tokens")
    async def test_create(self, refresh_tokens: list[RefreshTokenShema]) -> None:
        refresh_tokens = [CreateRefreshTokenShema.model_validate(el, from_attributes=True) for el in refresh_tokens]
        await super().test_create(refresh_tokens)


    @pytest.mark.usefixtures('refresh_tokens')
    @pytest.mark.parametrize(
            "index",
            [1, 2, 4]
    )
    async def test_create_existing(self, refresh_tokens: list[RefreshTokenShema], index: int) -> None: 
        refresh_tokens = [CreateRefreshTokenShema.model_validate(el, from_attributes=True) for el in refresh_tokens]
        await super().test_create_existing(refresh_tokens[index])


    @pytest.mark.usefixtures('refresh_tokens')
    @pytest.mark.parametrize(
            "index",
            [1, 2, 4]
    )
    async def test_get(self, refresh_tokens: list[RefreshTokenShema], index: int) -> None:
        await super().test_get("ident", refresh_tokens[index])

    
    @pytest.mark.parametrize(
            "filters, k",
            [
                (
                    {
                        "revoked": True
                    },
                    8
                ),
                (
                    {
                        "user_idents": [
                            "755d4fe7e8984fb997ef3de62ebf9313",
                            "275a20258e144cc9b1d1eda19ab7733b"
                        ],
                        "gen_dt_before": datetime(2024, 1, 1, 1, 1, 1)
                    },
                    6
                )
            ]
    )
    async def test_get_many(self, filters: dict, k: int) -> None:
        request_shema = RefreshTokenRequestShema.model_validate(
            filters
        )

        await super().test_get_many(k, request_shema)


    @pytest.mark.parametrize(
        "ident, data",
        [
            ("c37a83907992489eb37f2bee06d0115f", {"revoked": True}),
            ("4261f575ffdb4413a8215c92bc304092", {"user_ident": UUID("e4467703c51445c880a64a5b6fc56181")}),
            ("8765b8cce09b496087e25086ea1cb0dc", {"exp_dt": datetime(2024, 6, 1, 8, 38, 12, 906854)}),
        ]
    )
    async def test_update(self, ident: str, data: dict) -> None:
        await super().test_update(ident, data)


    @pytest.mark.usefixtures('refresh_tokens')
    @pytest.mark.parametrize(
            "index",
            [1, 2, 4]
    )
    async def test_delete(self, refresh_tokens: list[RefreshTokenShema], index: int) -> None:
        refresh_tokens = [CreateRefreshTokenShema.model_validate(el, from_attributes=True) for el in refresh_tokens]
        await super().test_delete(refresh_tokens[index])
