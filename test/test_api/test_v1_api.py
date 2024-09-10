from httpx import Cookies
import pytest
from copy import copy
from json import dumps, loads
from uuid import UUID

from client import client

from utils.DTOs import RefreshTokenData, UserData
from shemas import BaseUserShema
from funcs import test_data


@pytest.mark.usefixtures("prepare_db")
@pytest.mark.usefixtures("add_refresh_tokens")
@pytest.mark.usefixtures("add_users")
class TestAuthEndpoints:

    @pytest.mark.parametrize(
        "refresh_token",
        test_data.get_actual_refresh_tokens()[:3]
    )
    def test_get_current_user(self, refresh_token: RefreshTokenData):

        user = test_data.get_fake_user(refresh_token)

        res = client.post(
            f"auth/v1/current-user",
            cookies={"refresh_token": refresh_token.token}
        )

        assert res.status_code == 200

        assert BaseUserShema.model_validate(loads(res.content)) == BaseUserShema.model_validate(user, from_attributes=True)


    @pytest.mark.parametrize(
        "token_data",
        test_data.get_expired_refresh_tokens()[:10]
    )
    def test_failed_authenticate_by_expired_refresh_token(self, token_data: RefreshTokenData):

        res = client.post(
            "auth/v1/authenticate",
            cookies={
                "refresh_token": token_data.token
            }
        )

        assert res.status_code == 403
        assert res.text == '{"detail":"refresh token expired"}'


    @pytest.mark.parametrize(
        "token_data",
        test_data.get_revoked_refresh_tokens()[:5]
    )
    def test_failed_authenticate_by_revoked_refresh_token(self, token_data: RefreshTokenData):

        res = client.post(
            "auth/v1/authenticate",
            cookies={
                "refresh_token": token_data.token
            }
        )

        assert res.status_code == 403
        assert res.text == '{"detail":"revoked token"}'


    def test_failed_update_tokens_wothout_refresh_token(self):

        res = client.post(
            "auth/v1/update-tokens",
            cookies={}
        )

        assert res.status_code == 401
        assert res.text == '{"detail":"refresh token required"}'


    @pytest.mark.parametrize(
        "token_data",
        test_data.get_revoked_refresh_tokens()[:5]
    )
    def test_failed_update_tokens_by_revoked_refresh_token(self, token_data: RefreshTokenData):

        res = client.post(
            "auth/v1/update-tokens",
            cookies={
                "refresh_token": token_data.token
            }
        )

        assert res.status_code == 403
        assert res.text == '{"detail":"revoked token"}'
        

    def test_failed_authorizate_by_invalid_login(self):
        res = client.post(
            "auth/v1/authorizate",
            json={
                "login": "SomeInvalidLogin",
                "password": "QWE123df"
            }
        )

        assert res.status_code == 403
        assert res.text == '{"detail":"user (SomeInvalidLogin) not found"}'

    @pytest.mark.parametrize(
        "user",
        test_data.fake_users[:5]
    )
    def test_failed_authorizate_by_invalid_password(self, user: UserData):
        res = client.post(
            "auth/v1/authorizate",
            json={
                "login": user.login,
                "password": "QWE123df1111"
            }
        )

        assert res.status_code == 403
        assert res.text == '{"detail":"Invalid password"}'


    @pytest.mark.parametrize(
        "user",
        test_data.fake_users_dicts[:5]
    )
    def test_authorizate(self, user: dict):
        res = client.post(
            "auth/v1/authorizate",
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

        for cookie in res.cookies.jar:
            cookie.value == ""


    @pytest.mark.parametrize(
        "user",
        test_data.fake_user_generator.generate(5)
    )
    def test_create_user(self, user: dict):

        superuser_refresh_token = test_data.get_actual_superuser_refresh_token()

        res = client.post(
            "auth/v1/authenticate",
            cookies={
                "refresh_token": superuser_refresh_token.token
            }
        )

        client.cookies["access_token"] = res.cookies.get("access_token")

        del user["ident"]
        del user["hashed_password"]

        res = client.post(
            "v1/users",
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
            f"v1/users/{ident}",
            json=loads(dumps(data, default=str, sort_keys=True))
        )

        assert res.status_code == 200
        assert res.text == f"user {ident} successfully updated"


    @pytest.mark.parametrize(
        "user",
        test_data.fake_users[:3]
    )
    def test_delete_user(self, user: UserData):

        res = client.delete(
            f"v1/users/{user.ident}"
        )

        assert res.status_code == 200
        assert res.text == f"user {user.ident} successfully deleted"
