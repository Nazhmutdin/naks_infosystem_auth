from asyncio import run

import pytest
from httpx import AsyncClient, ASGITransport

from app.config import DBConfig
from app.infrastructure.database.models import Base
from app.main.app import app

from storage import storage
from utils import engine


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
    return storage.fake_users


@pytest.fixture
def users_dicts():
    return storage.fake_users_dicts


@pytest.fixture
def refresh_tokens():
    return storage.fake_refresh_tokens


@pytest.fixture
def refresh_tokens_dicts():
    return storage.fake_refresh_tokens_dicts


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
