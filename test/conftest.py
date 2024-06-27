from asyncio import run

import pytest

from shemas import *
from database import engine
from settings import Settings
from models import Base

from funcs import get_refresh_tokens, get_users, get_request_refresh_tokens


@pytest.fixture(scope="module")
def prepare_db():
    assert Settings.DB_NAME() == "rhi_test"

    async def start_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    run(start_db())


@pytest.fixture
def users() -> list[UserShema]:
    return get_users()


@pytest.fixture
def refresh_tokens() -> list[RefreshTokenShema]:
    return get_refresh_tokens()


@pytest.fixture
def request_refresh_tokens() -> list[RefreshTokenShema]:
    return get_request_refresh_tokens()
