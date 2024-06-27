import typing as t

from sqlalchemy.ext.asyncio import AsyncSession


class UOW:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __aenter__(self) -> t.Self:
        self.conn = await self.session.connection()
        return self


    async def __aexit__(self, *args) -> None:
        await self.rollback()
        await self.conn.close()
        await self.session.close()


    async def commit(self) -> None:
        await self.conn.commit()


    async def rollback(self) -> None:
        await self.conn.rollback()
