from asyncio import run

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from naks_library.committer import SqlAlchemyCommitter

from app.infrastructure.database.mappers import UserMapper, RefreshTokenMapper, PermissionMapper

from utils import engine
from storage import storage


@pytest.fixture(scope="class")
def add_users():

    async def add_users_async():
        async with AsyncSession(engine) as session:
            mapper = UserMapper(session)
            committer = SqlAlchemyCommitter(session)

            for user in storage.fake_users:
                await mapper.insert(user)
            
            await committer.commit()


    run(add_users_async())


@pytest.fixture(scope="class")
def add_refresh_tokens():

    async def add_refresh_tokens_async():
        async with AsyncSession(engine) as session:
            mapper = RefreshTokenMapper(session)
            committer = SqlAlchemyCommitter(session)

            for refresh_token in storage.fake_refresh_tokens:
                await mapper.insert(refresh_token)
            
            await committer.commit()
        

    run(add_refresh_tokens_async())



@pytest.fixture(scope="class")
def add_permissions():
    async def add_permissions_async():
        async with AsyncSession(engine) as session:
            mapper = PermissionMapper(session)
            committer = SqlAlchemyCommitter(session)

            for permission in storage.fake_permissions:
                await mapper.insert(permission)

            await committer.commit()
            

    run(add_permissions_async())
