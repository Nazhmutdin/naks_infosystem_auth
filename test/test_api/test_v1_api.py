from httpx import Cookies
import pytest
from copy import copy
from json import dumps, loads
from uuid import UUID

from client import client
from funcs import test_data
from app.application.dto import UserDTO, RefreshTokenDTO


@pytest.mark.usefixtures("prepare_db")
@pytest.mark.usefixtures("add_refresh_tokens")
@pytest.mark.usefixtures("add_users")
class TestAuthEndpoints:

    @pytest.mark.parametrize(
        "token_data",
        test_data.get_expired_refresh_tokens()[:10]
    )
    def test_failed_authenticate_by_expired_refresh_token(self, token_data: RefreshTokenDTO):

        client.cookies["refresh_token"] = token_data.token

        res = client.post(
            "auth/v1/authenticate"
        )

        assert res.status_code == 403


    @pytest.mark.parametrize(
        "token_data",
        test_data.get_revoked_refresh_tokens()[:5]
    )
    def test_failed_authenticate_by_revoked_refresh_token(self, token_data: RefreshTokenDTO):

        client.cookies["refresh_token"] = token_data.token

        res = client.post(
            "auth/v1/authenticate"
        )

        assert res.status_code == 403


    def test_failed_update_tokens_wothout_refresh_token(self):

        del client.cookies["refresh_token"]

        res = client.post(
            "auth/v1/update-tokens"
        )

        assert res.status_code == 401


    @pytest.mark.parametrize(
        "token_data",
        test_data.get_revoked_refresh_tokens()[:5]
    )
    def test_failed_update_tokens_by_revoked_refresh_token(self, token_data: RefreshTokenDTO):

        client.cookies["refresh_token"] = token_data.token

        res = client.post(
            "auth/v1/update-tokens"
        )

        assert res.status_code == 403
        

    def test_failed_authorizate_by_invalid_login(self):
        res = client.post(
            "auth/v1/login",
            json={
                "login": "SomeInvalidLogin",
                "password": "QWE123df"
            }
        )

        assert res.status_code == 404


    @pytest.mark.parametrize(
        "user",
        test_data.fake_users[:5]
    )
    def test_failed_authorizate_by_invalid_password(self, user: UserDTO):
        res = client.post(
            "auth/v1/login",
            json={
                "login": user.login,
                "password": "QWE123df1111"
            }
        )

        assert res.status_code == 403


    @pytest.mark.parametrize(
        "user",
        test_data.fake_users_dicts[:5]
    )
    def test_authorizate(self, user: dict):
        res = client.post(
            "auth/v1/login",
            json={
                "login": user["login"],
                "password": user["password"]
            }
        )

        assert res.status_code == 200

        client.cookies = Cookies(
            {
                "access_token": res.cookies.get("access_token"),
                "refresh_token": res.cookies.get("refresh_token")
            }
        )


    def test_authenticate(self):
        access_token = copy(client.cookies["access_token"])

        res = client.post(
            "auth/v1/authenticate",
        )

        assert res.status_code == 200

        assert res.cookies.get("access_token") != access_token
    
    
    def test_update_tokens(self):
        refresh_token = copy(client.cookies["refresh_token"])

        res = client.post(
            "auth/v1/update-tokens",
        )

        assert res.status_code == 200

        assert res.cookies.get("refresh_token") != refresh_token

        client.cookies["refresh_token"] = res.cookies.get("refresh_token")


    def test_validate_access_token(self):

        res = client.post(
            "auth/v1/validate-access",
        )

        assert res.status_code == 200


    def test_logout(self):

        res = client.post(
            "auth/v1/logout"
        )

        assert res.status_code == 200


    @pytest.mark.parametrize(
        "user",
        test_data.fake_user_generator.generate(5)
    )
    def test_create_user(self, user: dict):

        superuser_refresh_token = test_data.get_actual_superuser_refresh_token()

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
        "ident, data",
        [(user.ident, new_user_data) for user, new_user_data in zip(test_data.fake_users[:5], test_data.fake_user_generator.generate(5))]
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
        test_data.fake_users[:3]
    )
    def test_delete_user(self, user: UserDTO):

        res = client.delete(
            f"v1/user/{user.ident}"
        )

        assert res.status_code == 200
        assert res.text == f"user {user.ident} successfully deleted"
