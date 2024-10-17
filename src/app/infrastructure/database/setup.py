from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy import NullPool

from app.configs import DBConfig


def create_engine(echo: bool = False) -> AsyncEngine:
    return create_async_engine(
        DBConfig.DB_URL(),
        poolclass=NullPool,
        echo=echo
    )


def create_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, autocommit=False, autoflush=False, expire_on_commit=False)
