from asyncio import run

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from main.dependencies import container, dump_create_user_interactor, dump_create_refresh_token_interactor
from funcs import test_data


@pytest.fixture(scope="class")
def add_users():

    async def add_users_async():
        async with AsyncSession(container.engine) as session:
            create = await dump_create_user_interactor(session)

            for user in test_data.fake_users:
                await create(user)

    run(add_users_async())


@pytest.fixture(scope="class")
def add_refresh_tokens():

    async def add_refresh_tokens_async():
        async with AsyncSession(container.engine) as session:
            create = await dump_create_refresh_token_interactor(session)

            for refresh_token in test_data.fake_refresh_tokens:
                await create(refresh_token)
        
    run(add_refresh_tokens_async())
