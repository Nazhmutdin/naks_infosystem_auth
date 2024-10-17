from asyncio import run

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from naks_library.commiter import SqlAlchemyCommitter

from app.application.interactors import CreateUserInteractor, CreateRefreshTokenInteractor
from app.infrastructure.database.mappers import UserMapper, RefreshTokenMapper
from funcs import test_data, engine


@pytest.fixture(scope="class")
def add_users():

    async def add_users_async():
        async with AsyncSession(engine) as session:
            mapper = UserMapper(session)
            committer = SqlAlchemyCommitter(session)
            create = CreateUserInteractor(
                mapper,
                committer
            )

            for user in test_data.fake_users:
                await create(user)

    run(add_users_async())


@pytest.fixture(scope="class")
def add_refresh_tokens():

    async def add_refresh_tokens_async():
        async with AsyncSession(engine) as session:
            mapper = RefreshTokenMapper(session)
            committer = SqlAlchemyCommitter(session)
            create = CreateRefreshTokenInteractor(
                mapper,
                committer
            )

            for refresh_token in test_data.fake_refresh_tokens:
                await create(refresh_token)
        
    run(add_refresh_tokens_async())
