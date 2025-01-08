from typing import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from naks_library.commiter import SqlAlchemyCommitter

import redis.asyncio as redis

from app.infrastructure.database.setup import create_engine, create_session_maker
from app.infrastructure.redis.setup import create_redis


class CoreProvider(Provider):

    @provide(scope=Scope.APP)
    def get_session_pool(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return create_session_maker(engine)


    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return create_engine()


    @provide(scope=Scope.REQUEST)
    async def get_uow(
        self, session_pool: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[SqlAlchemyCommitter]:
        async with session_pool() as session:
            yield SqlAlchemyCommitter(session)


    @provide(scope=Scope.APP)
    async def provide_redis(
        self
    ) -> AsyncIterator[redis.Redis]:
        async with create_redis() as redis:
            yield redis
