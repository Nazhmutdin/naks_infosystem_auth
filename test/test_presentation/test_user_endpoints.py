import pytest
from json import dumps, loads
from uuid import UUID

from httpx import AsyncClient

from storage import storage
from app.application.dto import UserDTO


@pytest.mark.usefixtures("prepare_db")
@pytest.mark.usefixtures("add_refresh_tokens")
@pytest.mark.usefixtures("add_permissions")
@pytest.mark.usefixtures("add_users")
class TestUserEndpoints:

    @pytest.mark.parametrize(
        "user",
        storage.fake_user_generator.generate_test_data(1)
    )
    @pytest.mark.anyio
    async def test_create_user_forbidden(self, user: dict, client: AsyncClient):

        refresh_token = storage.get_actual_usual_user_refresh_token()

        client.cookies["refresh_token"] = refresh_token.token

        res = await client.post(
            "auth/v1/authenticate"
        )

        client.cookies["access_token"] = res.cookies.get("access_token")

        del user["ident"]
        del user["hashed_password"]

        res = await client.post(
            "v1/user/",
            headers={
                "x-original-method": "POST",
                "x-original-uri": "/v1/user"
            },
            json=loads(dumps(user, default=str, sort_keys=True))
        )

        assert res.status_code == 403


    @pytest.mark.parametrize(
        "ident",
        [user.ident for user in storage.fake_users]
    )
    @pytest.mark.anyio
    async def test_get_user_forbidden(self, ident: UUID, client: AsyncClient):

        res = await client.get(
            "v1/user/",
            params={
                "ident": ident
            },
            headers={
                "x-original-method": "GET",
                "x-original-uri": "/v1/user"
            }
        )

        assert res.status_code == 403


    @pytest.mark.parametrize(
        "ident, data",
        [(user.ident, new_user_data) for user, new_user_data in zip(storage.fake_users[:5], storage.fake_user_generator.generate_test_data(5))]
    )
    @pytest.mark.anyio
    async def test_update_user_forbidden(self, ident: UUID, data: dict, client: AsyncClient):

        del data["ident"]

        res = await client.patch(
            "v1/user/",
            params={
                "ident": ident
            },
            headers={
                "x-original-method": "PATCH",
                "x-original-uri": "/v1/user"
            },
            json=loads(dumps(data, default=str, sort_keys=True))
        )

        assert res.status_code == 403


    @pytest.mark.parametrize(
        "user",
        storage.fake_users[1:]
    )
    @pytest.mark.anyio
    async def test_delete_user_forbidden(self, user: UserDTO, client: AsyncClient):

        res = await client.delete(
            "v1/user/",
            params={
                "ident": user.ident
            },
            headers={
                "x-original-method": "DELETE",
                "x-original-uri": "/v1/user"
            }
        )

        assert res.status_code == 403


    @pytest.mark.parametrize(
        "user",
        storage.fake_user_generator.generate_test_data(5)
    )
    @pytest.mark.anyio
    async def test_create_user(self, user: dict, client: AsyncClient):

        superuser_refresh_token = storage.get_actual_superuser_refresh_token()

        client.cookies["refresh_token"] = superuser_refresh_token.token

        res = await client.post(
            "auth/v1/authenticate"
        )

        client.cookies["access_token"] = res.cookies.get("access_token")

        del user["ident"]
        del user["hashed_password"]

        res = await client.post(
            "v1/user/",
            headers={
                "x-original-method": "POST",
                "x-original-uri": "v1/user"
            },
            json=loads(dumps(user, default=str, sort_keys=True))
        )

        assert res.status_code == 200
        assert res.text == "user successfully created"


    @pytest.mark.parametrize(
        "ident",
        [user.ident for user in storage.fake_users]
    )
    @pytest.mark.anyio
    async def test_get_user(self, ident: UUID, client: AsyncClient):

        res = await client.get(
            "v1/user/",
            params={
                "ident": ident
            },
            headers={
                "x-original-method": "GET",
                "x-original-uri": "v1/user"
            }
        )

        assert res.status_code == 200


    @pytest.mark.parametrize(
        "ident, data",
        [(user.ident, new_user_data) for user, new_user_data in zip(storage.fake_users[:5], storage.fake_user_generator.generate_test_data(5))]
    )
    @pytest.mark.anyio
    async def test_update_user(self, ident: UUID, data: dict, client: AsyncClient):

        del data["ident"]

        res = await client.patch(
            "v1/user/",
            params={
                "ident": ident
            },
            headers={
                "x-original-method": "PATCH",
                "x-original-uri": "v1/user"
            },
            json=loads(dumps(data, default=str, sort_keys=True))
        )

        assert res.status_code == 200
        assert res.text == f"user {ident} successfully updated"


    @pytest.mark.parametrize(
        "user",
        storage.fake_users[1:]
    )
    @pytest.mark.anyio
    async def test_delete_user(self, user: UserDTO, client: AsyncClient):

        res = await client.delete(
            "v1/user/",
            params={
                "ident": user.ident
            },
            headers={
                "x-original-method": "DELETE",
                "x-original-uri": "v1/user"
            }
        )

        assert res.status_code == 200
        assert res.text == f"user {user.ident} successfully deleted"
