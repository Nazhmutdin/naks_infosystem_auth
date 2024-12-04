import pathlib
import json
import asyncio

import click
from naks_library.commiter import SqlAlchemyCommitter

from app.application.dto import CreatePermissionDTO, CreateUserDTO
from app.infrastructure.database.setup import create_engine, create_session_maker
from app.infrastructure.database.mappers import PermissionMapper


@click.group()
def cli(): ...


engine = create_engine()
session_maker = create_session_maker(engine)


async def add_permissions(data: list[CreatePermissionDTO]):
    async with session_maker() as session:
        committer = SqlAlchemyCommitter(session)
        mapper = PermissionMapper(session)

        for el in data:
            await mapper.insert(el)

        await committer.commit()


@cli.command("add-permissions")
@click.option("--src-path", "-sp", type=str)
def add_permissions_command(
    src_path: str,
):
    path = pathlib.Path(src_path)

    if not path.exists():
        raise ValueError(f"path ({src_path}) not exists")
    
    data = [CreatePermissionDTO(**el) for el in json.load(open(path, "r", encoding="utf-8"))]

    asyncio.run(add_permissions(data))


async def add_users(data: list[CreateUserDTO]):
    async with session_maker() as session:
        committer = SqlAlchemyCommitter(session)
        mapper = PermissionMapper(session)

        for el in data:
            await mapper.insert(el)

        await committer.commit()


@cli.command("add-users")
@click.option("--src-path", "-sp", type=str)
def add_users_command(
    src_path: str,
):
    path = pathlib.Path(src_path)

    if not path.exists():
        raise ValueError(f"path ({src_path}) not exists")
    
    data = [CreateUserDTO(**el) for el in json.load(open(path, "r", encoding="utf-8"))]

    asyncio.run(add_users(data))


if __name__ == "__main__":
    cli()
