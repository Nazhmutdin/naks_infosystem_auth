import pytest
from json import dumps, loads
from uuid import UUID

from client import client
from storage import storage
from app.application.dto import UserDTO

@pytest.mark.usefixtures("prepare_db")
@pytest.mark.usefixtures("add_refresh_tokens")
@pytest.mark.usefixtures("add_permissions")
@pytest.mark.usefixtures("add_users")
class TestAuthEndpoints:

    @pytest.mark.parametrize(
        "user",
        storage.fake_user_generator.generate_test_data(1)
    )
    def test_create_user_forbidden(self, user: dict):

        refresh_token = storage.get_actual_usual_user_refresh_token()

        client.cookies["refresh_token"] = refresh_token.token

        res = client.post(
            "auth/v1/authenticate"
        )

        client.cookies["access_token"] = res.cookies.get("access_token")

        del user["ident"]
        del user["hashed_password"]

        res = client.post(
            "v1/user",
            json=loads(dumps(user, default=str, sort_keys=True))
        )

        assert res.status_code == 403


    @pytest.mark.parametrize(
        "ident",
        [user.ident for user in storage.fake_users]
    )
    def test_get_user_forbidden(self, ident: UUID):

        res = client.get(
            f"v1/user/{ident.hex}"
        )

        assert res.status_code == 403


    @pytest.mark.parametrize(
        "ident, data",
        [(user.ident, new_user_data) for user, new_user_data in zip(storage.fake_users[:5], storage.fake_user_generator.generate_test_data(5))]
    )
    def test_update_user_forbidden(self, ident: UUID, data: dict):

        del data["ident"]

        res = client.patch(
            f"v1/user/{ident}",
            json=loads(dumps(data, default=str, sort_keys=True))
        )

        assert res.status_code == 403


    @pytest.mark.parametrize(
        "user",
        storage.fake_users[1:]
    )
    def test_delete_user_forbidden(self, user: UserDTO):

        res = client.delete(
            f"v1/user/{user.ident}"
        )

        assert res.status_code == 403


    @pytest.mark.parametrize(
        "user",
        storage.fake_user_generator.generate_test_data(5)
    )
    def test_create_user(self, user: dict):

        superuser_refresh_token = storage.get_actual_superuser_refresh_token()

        client.cookies["refresh_token"] = superuser_refresh_token.token

        res = client.post(
            "auth/v1/authenticate"
        )

        client.cookies["access_token"] = res.cookies.get("access_token")

        del user["ident"]
        del user["hashed_password"]

        res = client.post(
            "v1/user",
            json=loads(dumps(user, default=str, sort_keys=True))
        )

        assert res.status_code == 200
        assert res.text == "user successfully created"


    @pytest.mark.parametrize(
        "ident",
        [user.ident for user in storage.fake_users]
    )
    def test_get_user(self, ident: UUID):

        res = client.get(
            f"v1/user/{ident.hex}"
        )

        assert res.status_code == 200


    @pytest.mark.parametrize(
        "ident, data",
        [(user.ident, new_user_data) for user, new_user_data in zip(storage.fake_users[:5], storage.fake_user_generator.generate_test_data(5))]
    )
    def test_update_user(self, ident: UUID, data: dict):

        del data["ident"]

        res = client.patch(
            f"v1/user/{ident}",
            json=loads(dumps(data, default=str, sort_keys=True))
        )

        assert res.status_code == 200
        assert res.text == f"user {ident} successfully updated"


    @pytest.mark.parametrize(
        "user",
        storage.fake_users[1:]
    )
    def test_delete_user(self, user: UserDTO):

        res = client.delete(
            f"v1/user/{user.ident}"
        )

        assert res.status_code == 200
        assert res.text == f"user {user.ident} successfully deleted"
