from asyncio import run

import pytest

from configs import DBConfig
from infrastructure.database.models import Base
from main.dependencies import container

from funcs import test_data


@pytest.fixture(scope="module")
def prepare_db():
    assert DBConfig.DB_NAME() == "rhi_test_auth"

    async def start_db():
        async with container.engine.begin() as conn:
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
