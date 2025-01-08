from httpx import Cookies, AsyncClient
import pytest
from copy import copy

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
    @pytest.mark.anyio
    async def test_failed_authenticate_by_expired_refresh_token(self, token_data: RefreshTokenDTO, client: AsyncClient):

        client.cookies["refresh_token"] = token_data.token

        res = await client.post(
            "auth/v1/authenticate"
        )

        assert res.status_code == 403


    @pytest.mark.parametrize(
        "token_data",
        storage.get_revoked_refresh_tokens()[:5]
    )   
    @pytest.mark.anyio
    async def test_failed_authenticate_by_revoked_refresh_token(self, token_data: RefreshTokenDTO, client: AsyncClient):

        client.cookies["refresh_token"] = token_data.token

        res = await client.post(
            "auth/v1/authenticate"
        )

        assert res.status_code == 403


    @pytest.mark.anyio
    async def test_failed_update_tokens_wothout_refresh_token(self, client: AsyncClient):

        del client.cookies["refresh_token"]

        res = await client.post(
            "auth/v1/update-tokens"
        )

        assert res.status_code == 401


    @pytest.mark.parametrize(
        "token_data",
        storage.get_revoked_refresh_tokens()[:5]
    )   
    @pytest.mark.anyio
    async def test_failed_update_tokens_by_revoked_refresh_token(self, token_data: RefreshTokenDTO, client: AsyncClient):

        client.cookies["refresh_token"] = token_data.token

        res = await client.post(
            "auth/v1/update-tokens"
        )

        assert res.status_code == 403
        

    @pytest.mark.anyio
    async def test_failed_authorizate_by_invalid_login(self, client: AsyncClient):
        res = await client.post(
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
    @pytest.mark.anyio
    async def test_failed_authorizate_by_invalid_password(self, user: UserDTO, client: AsyncClient):
        res = await client.post(
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
    @pytest.mark.anyio
    async def test_authorizate(self, user: dict, client: AsyncClient):
        res = await client.post(
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


    @pytest.mark.anyio
    async def test_authenticate(self, client: AsyncClient):
        access_token = copy(client.cookies["access_token"])

        res = await client.post(
            "auth/v1/authenticate",
        )

        assert res.status_code == 200

        assert res.cookies.get("access_token") != access_token
    

    @pytest.mark.anyio
    async def test_update_tokens(self, client: AsyncClient):
        refresh_token = copy(client.cookies["refresh_token"])

        res = await client.post(
            "auth/v1/update-tokens",
        )

        assert res.status_code == 200

        assert res.cookies.get("refresh_token") != refresh_token

        client.cookies["refresh_token"] = res.cookies.get("refresh_token")


    @pytest.mark.parametrize(
        "user",
        storage.fake_users_dicts[1:]
    )   
    @pytest.mark.anyio
    async def test_aproved_access(self, user: dict, client: AsyncClient):
        permissions = storage.get_user_permission(user["ident"])

        res = await client.post(
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
                uri = "/v1/personal"
            elif uri == "personal_naks_certification_data":
                uri = "/v1/personal-naks-certification"
            elif uri == "ndt_data":
                uri = "/v1/ndt"
            elif uri == "acst_data":
                uri = "/v1/acst"
             

            res = await client.post(
                "auth/v1/validate-access",

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
    @pytest.mark.anyio
    async def test_denied_access(self, user: dict, client: AsyncClient):
        permissions = storage.get_user_permission(user["ident"])

        res = await client.post(
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
                "is_super_user",
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
                uri = "/v1/personal"
            elif uri == "personal_naks_certification_data":
                uri = "/v1/personal-naks-certification"
            elif uri == "ndt_data":
                uri = "/v1/ndt"
            elif uri == "acst_data":
                uri = "/v1/acst"
             

            res = await client.post(
                "auth/v1/validate-access",

                headers={
                    "x-original-method": method,
                    "x-original-uri": uri
                }
            )

            assert res.status_code == 403


    @pytest.mark.anyio
    async def test_logout(self, client: AsyncClient):

        res = await client.post(
            "auth/v1/logout"
        )

        assert res.status_code == 200