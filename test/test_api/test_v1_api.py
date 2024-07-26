from httpx import Cookies
import pytest
from copy import copy

from client import client


@pytest.mark.usefixtures("prepare_db")
@pytest.mark.usefixtures("add_refresh_tokens")
@pytest.mark.usefixtures("add_users")
class TestAuthEndpoints:

    def test_failed_authenticate_by_expired_refresh_token(self):

        res = client.post(
            "auth/v1/authenticate",
            cookies={
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudCI6IjU0MzQxN2IwNTk5MTQwYjFhYjk3OTc5OGNjZTE3MWUwIiwidXNlcl9pZGVudCI6IjI3NWEyMDI1OGUxNDRjYzliMWQxZWRhMTlhYjc3MzNiIiwiZ2VuX2R0IjoiMjAyNC8wNy8yMSwgMTc6MTA6MjUiLCJleHBfZHQiOiIyMDI0LzA3LzIyLCAxNzoxMDoyNSJ9.Ddi9rNGGU3AfqxwaGx-JHDOUphmKUwGOlfeDgd1gGQw"
            }
        )

        assert res.status_code == 400
        assert res.text == '{"detail":"refresh token expired"}'


    def test_failed_authenticate_by_revoked_refresh_token(self):

        res = client.post(
            "auth/v1/authenticate",
            cookies={
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudCI6ImMzN2E4MzkwNzk5MjQ4OWViMzdmMmJlZTA2ZDAxMTVmIiwidXNlcl9pZGVudCI6Ijc1NWQ0ZmU3ZTg5ODRmYjk5N2VmM2RlNjJlYmY5MzEzIiwiZ2VuX2R0IjoiMjAyNC8wNy8yNSwgMTc6MTA6MjUiLCJleHBfZHQiOiIyMDI0LzA3LzI2LCAxNzoxMDoyNSJ9.OPpWPvbCSGNpBJh3QOcvL7FTKpK0GvWWBkoEZm_o_tI"
            }
        )

        assert res.status_code == 400
        assert res.text == '{"detail":"revoked token"}'


    def test_failed_update_tokens_wothout_refresh_token(self):

        res = client.post(
            "auth/v1/update-tokens",
            cookies={}
        )

        assert res.status_code == 400
        assert res.text == '{"detail":"refresh token required"}'


    def test_failed_update_tokens_by_revoked_refresh_token(self):

        res = client.post(
            "auth/v1/update-tokens",
            cookies={
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudCI6ImMzN2E4MzkwNzk5MjQ4OWViMzdmMmJlZTA2ZDAxMTVmIiwidXNlcl9pZGVudCI6Ijc1NWQ0ZmU3ZTg5ODRmYjk5N2VmM2RlNjJlYmY5MzEzIiwiZ2VuX2R0IjoiMjAyNC8wNy8yNSwgMTc6MTA6MjUiLCJleHBfZHQiOiIyMDI0LzA3LzI2LCAxNzoxMDoyNSJ9.OPpWPvbCSGNpBJh3QOcvL7FTKpK0GvWWBkoEZm_o_tI"
            }
        )

        assert res.status_code == 400
        assert res.text == '{"detail":"revoked token"}'
        

    def test_failed_authorizate_by_invalid_login(self):
        res = client.post(
            "auth/v1/authorizate",
            json={
                "login": "SomeInvalidLogin",
                "password": "QWE123df"
            }
        )

        assert res.status_code == 400
        assert res.text == '{"detail":"user (SomeInvalidLogin) not found"}'


    def test_failed_authorizate_by_invalid_password(self):
        res = client.post(
            "auth/v1/authorizate",
            json={
                "login": "TestUser1",
                "password": "QWE123df1111"
            }
        )

        assert res.status_code == 400
        assert res.text == '{"detail":"Invalid password"}'


    def test_authorizate(self):
        res = client.post(
            "auth/v1/authorizate",
            json={
                "login": "TestUser1",
                "password": "QWE123df"
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
    
    
    def test_update_token(self):
        refresh_token = copy(client.cookies["refresh_token"])

        res = client.post(
            "auth/v1/update-tokens",
        )

        assert res.status_code == 200

        assert res.cookies.get("refresh_token") != refresh_token


    def test_validate_access_token(self):

        res = client.post(
            "auth/v1/validate-access",
        )

        assert res.status_code == 200
