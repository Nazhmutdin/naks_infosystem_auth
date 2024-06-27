from asyncio import run

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from services.db_services import UserDBService, RefreshTokenDBService
from shemas import CreateUserShema, CreateRefreshTokenShema
from database import engine
from funcs import get_users, get_refresh_tokens


@pytest.fixture(scope="class")
def add_users():

    async def add_users_async():
        service = UserDBService(AsyncSession(engine))
        
        await service.add(*[CreateUserShema.model_validate(user, from_attributes=True) for user in get_users()])
    
    run(add_users_async())


@pytest.fixture(scope="class")
def add_refresh_tokens():

    async def add_refresh_tokens_async():
        service = RefreshTokenDBService(AsyncSession(engine))
        
        await service.add(*[CreateRefreshTokenShema.model_validate(token, from_attributes=True) for token in get_refresh_tokens()])
    
    run(add_refresh_tokens_async())
