from asyncio import run

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from services.db_services import UserDBService, RefreshTokenDBService
from shemas import CreateUserShema, CreateRefreshTokenShema
from database import engine
from funcs import test_data


@pytest.fixture(scope="class")
def add_users():

    async def add_users_async():
        service = UserDBService()
        
        await service.insert(AsyncSession(engine), *[CreateUserShema.model_validate(user) for user in test_data.fake_users_dicts])
    
    run(add_users_async())


@pytest.fixture(scope="class")
def add_refresh_tokens():

    async def add_refresh_tokens_async():
        service = RefreshTokenDBService()
        
        await service.insert(AsyncSession(engine), *[CreateRefreshTokenShema.model_validate(token) for token in test_data.fake_refresh_tokens_dicts])
    
    run(add_refresh_tokens_async())
