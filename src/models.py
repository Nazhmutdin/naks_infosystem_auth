from datetime import datetime
import typing as t
import uuid

from sqlalchemy.orm import Mapped, DeclarativeBase, attributes
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.schema import Index
import sqlalchemy as sa
from naks_library.funcs import is_uuid


__all__ = [
    "Base",
    "UserModel",
    "RefreshTokenModel"
]

class Base(DeclarativeBase): 

    @classmethod
    async def get(cls, conn: AsyncConnection, ident: uuid.UUID | str):
        stmt = cls._dump_get_stmt(ident)
        response = await conn.execute(stmt)
        result = response.mappings().one_or_none()

        return result
        

    @classmethod
    async def get_many(cls, conn: AsyncConnection, expression: sa.ColumnElement, limit: int, offset: int):
        stmt = cls._dump_get_many_stmt(expression)

        amount = await cls.count(conn, stmt)

        if limit:
            stmt = stmt.limit(limit)

        if offset:
            stmt = stmt.offset(offset)
        
        response = await conn.execute(stmt)

        result = response.mappings().all()
        
        return (result, amount)
        

    @classmethod
    async def create(cls, data: list[dict], conn: AsyncConnection):
        stmt = cls._dump_create_stmt(
            data
        )

        await conn.execute(stmt)


    @classmethod
    async def update(cls, conn: AsyncConnection, ident: uuid.UUID | str, data: dict[str, t.Any]):
        stmt = cls._dump_update_stmt(ident, data)
        await conn.execute(stmt)


    @classmethod
    async def delete(cls, conn: AsyncConnection, ident: uuid.UUID | str):
        stmt = cls._dump_delete_stmt(ident)
        await conn.execute(stmt)


    @classmethod
    async def count(cls, conn: AsyncConnection, stmt: sa.Select | None = None):
        if isinstance(stmt, sa.ColumnElement):
            stmt.select(sa.func.count())

            return (await conn.execute(stmt)).scalar_one()

        else:
            return (await conn.execute(sa.select(sa.func.count()).select_from(cls).distinct())).scalar_one()


    @classmethod
    def _get_column(cls, ident: str | uuid.UUID):
        return sa.inspect(cls).primary_key[0]


    @classmethod
    def _dump_create_stmt(cls, data: list[dict[str, t.Any]]):
        return sa.insert(cls).values(
            data
        )


    @classmethod
    def _dump_get_stmt(cls, ident: str | uuid.UUID):
        return sa.select(cls).where(
            cls._get_column(ident) == ident
        )


    @classmethod
    def _dump_get_many_stmt(cls, expression: sa.ColumnExpressionArgument):
        return sa.select(cls).filter(expression)
    

    @classmethod
    def _dump_update_stmt(cls, ident: str | uuid.UUID, data: dict[str, t.Any]):
        return sa.update(cls).where(
            cls._get_column(ident) == ident
        ).values(
            **data
        )


    @classmethod
    def _dump_delete_stmt(cls, ident: str | uuid.UUID):
        return sa.delete(cls).where(
            cls._get_column(ident) == ident
        )


class UserModel(Base):
    __tablename__ = "user_table"

    ident: Mapped[uuid.UUID] = sa.Column(sa.UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = sa.Column(sa.String(), nullable=False)
    login: Mapped[str] = sa.Column(sa.String(), unique=True, nullable=False)
    hashed_password: Mapped[str] = sa.Column(sa.String(), nullable=False)
    email: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    sign_dt: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)
    update_dt: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)
    login_dt: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)
    is_superuser: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False)

    __table_args__ = (
        Index("user_ident_idx", ident),
    )
    

    @classmethod
    def _get_column(cls, ident: str | uuid.UUID) -> attributes.InstrumentedAttribute:
        if is_uuid(ident):
            return cls.ident
        
        return cls.login


class RefreshTokenModel(Base):
    __tablename__ = "refresh_token_table"

    ident: Mapped[uuid.UUID] = sa.Column(sa.UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_ident: Mapped[uuid.UUID] = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey("user_table.ident", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    token: Mapped[str] = sa.Column(sa.String(), nullable=False, unique=True)
    revoked: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False)
    exp_dt: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)
    gen_dt: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)

    __table_args__ = (
        Index("refresh_token_ident_idx", ident),
        Index("token_idx", token),
        Index("revoked_idx", revoked),
    )
    

    @classmethod
    def _get_column(cls, ident: str | uuid.UUID) -> attributes.InstrumentedAttribute:
        if is_uuid(ident):
            return RefreshTokenModel.ident
        
        return RefreshTokenModel.token
