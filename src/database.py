from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import NullPool

from src.settings import Settings


DB_URL = "postgresql+asyncpg://{0}:{1}@{2}:{3}/{4}".format(
    Settings.USER(), 
    Settings.DB_PASSWORD(), 
    Settings.HOST(), 
    Settings.PORT(), 
    Settings.DB_NAME()
)


engine = create_async_engine(
    DB_URL,
    poolclass=NullPool
)

session_maker = async_sessionmaker(engine, autocommit=False, autoflush=False, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session
