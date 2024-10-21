from typing import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from naks_library.commiter import SqlAlchemyCommitter

from app.infrastructure.database.setup import create_engine, create_session_maker


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
