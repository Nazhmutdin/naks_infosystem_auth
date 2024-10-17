from asyncio import run

import pytest

from app.configs import DBConfig
from app.infrastructure.database.models import Base

from funcs import test_data, engine


@pytest.fixture(scope="module")
def prepare_db():
    assert DBConfig.DB_NAME() == "rhi_test_auth"

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
