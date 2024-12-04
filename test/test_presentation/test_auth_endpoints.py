from httpx import Cookies
import pytest
from copy import copy

from client import client
from storage import storage
from app.application.dto import UserDTO, RefreshTokenDTO


@pytest.mark.usefixtures("prepare_db")
@pytest.mark.usefixtures("add_refresh_tokens")
@pytest.mark.usefixtures("add_permissions")
@pytest.mark.usefixtures("add_users")
class TestAuthEndpoints:

    @pytest.mark.parametrize(
        "token_data",
        storage.get_expired_refresh_tokens()[:10]
    )
    def test_failed_authenticate_by_expired_refresh_token(self, token_data: RefreshTokenDTO):

        client.cookies["refresh_token"] = token_data.token

        res = client.post(
            "auth/v1/authenticate"
        )

        assert res.status_code == 403


    @pytest.mark.parametrize(
        "token_data",
        storage.get_revoked_refresh_tokens()[:5]
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
        storage.get_revoked_refresh_tokens()[:5]
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
        storage.fake_users[:5]
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
        storage.fake_users_dicts[:5]
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


    @pytest.mark.parametrize(
        "user",
        storage.fake_users_dicts[1:]
    )
    def test_aproved_access(self, user: dict):
        permissions = storage.get_user_permission(user["ident"])

        res = client.post(
            "auth/v1/login",
            json={
                "login": user["login"],
                "password": user["password"]
            }
        )

        client.cookies = Cookies(
            {
                "access_token": res.cookies.get("access_token"),
                "refresh_token": res.cookies.get("refresh_token")
            }
        )


        for key, value in permissions.__dict__.items():

            if key in [
                "ident", 
                "user_ident", 
                "acst_file_download", 
                "acst_file_upload", 
                "personal_naks_certification_file_download", 
                "personal_naks_certification_file_upload", 
                "personal_naks_protocol_file_download", 
                "personal_naks_protocol_file_upload"
            ]:
                continue

            if not value:
                continue

            key_items = key.split("_")

            method = key_items[-1]
            uri = "_".join(key_items[:-1])

            if method == "get":
                method = "GET"
            elif method == "create":
                method = "POST"
            elif method == "update":
                method = "PATCH"
            elif method == "delete":
                method = "DELETE"

            if uri == "personal_data":
                uri = "v1/personal"
            elif uri == "personal_naks_certification_data":
                uri = "v1/personal-naks-certification"
            elif uri == "ndt_data":
                uri = "v1/ndt"
            elif uri == "acst_data":
                uri = "v1/acst"
             

            res = client.post(
                "auth/v1/validate-data-access",

                headers={
                    "x-original-method": method,
                    "x-original-uri": uri
                }
            )

            assert res.status_code == 200


    @pytest.mark.parametrize(
        "user",
        storage.fake_users_dicts[1:]
    )
    def test_denied_access(self, user: dict):
        permissions = storage.get_user_permission(user["ident"])

        res = client.post(
            "auth/v1/login",
            json={
                "login": user["login"],
                "password": user["password"]
            }
        )

        client.cookies = Cookies(
            {
                "access_token": res.cookies.get("access_token"),
                "refresh_token": res.cookies.get("refresh_token")
            }
        )


        for key, value in permissions.__dict__.items():

            if key in [
                "ident", 
                "user_ident", 
                "acst_file_download", 
                "acst_file_upload", 
                "personal_naks_certification_file_download", 
                "personal_naks_certification_file_upload", 
                "personal_naks_protocol_file_download", 
                "personal_naks_protocol_file_upload"
            ]:
                continue

            if value:
                continue

            key_items = key.split("_")

            method = key_items[-1]
            uri = "_".join(key_items[:-1])

            if method == "get":
                method = "GET"
            elif method == "create":
                method = "POST"
            elif method == "update":
                method = "PATCH"
            elif method == "delete":
                method = "DELETE"

            if uri == "personal_data":
                uri = "v1/personal"
            elif uri == "personal_naks_certification_data":
                uri = "v1/personal-naks-certification"
            elif uri == "ndt_data":
                uri = "v1/ndt"
            elif uri == "acst_data":
                uri = "v1/acst"
             

            res = client.post(
                "auth/v1/validate-data-access",

                headers={
                    "x-original-method": method,
                    "x-original-uri": uri
                }
            )

            assert res.status_code == 403


    def test_logout(self):

        res = client.post(
            "auth/v1/logout"
        )

        assert res.status_code == 200