from asyncio import run

import pytest

from shemas import *
from database import engine
from settings import Settings
from models import Base

from funcs import test_data, get_request_refresh_tokens


@pytest.fixture(scope="module", autouse=True)
def prepare_db():
    assert Settings.DB_NAME() == "rhi_test_auth"

    async def start_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    run(start_db())


@pytest.fixture
def users():
    return test_data.fake_users

@pytest.fixture
def users_dicts():
    return test_data.fake_users_dicts


@pytest.fixture
def refresh_tokens():
    return test_data.fake_refresh_tokens


@pytest.fixture
def refresh_tokens_dicts():
    return test_data.fake_refresh_tokens_dicts


@pytest.fixture
def request_refresh_tokens() -> list[RefreshTokenShema]:
    return get_request_refresh_tokens()
