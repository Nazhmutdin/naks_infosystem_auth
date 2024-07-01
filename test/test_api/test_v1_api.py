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
            "api/auth/v1/authenticate",
            cookies={
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJnZW5fZHQiOiIyMDI0LzA1LzI3LCAxMzozODoxMiIsImV4cF9kdCI6IjIwMjQvMDUvMjgsIDEzOjM4OjEyIiwiaWRlbnQiOiJjNGIyNTY2NzdhYWM0NWE5OTRlZjVlZTQxNGY0NDc3MiIsInVzZXJfaWRlbnQiOiJiN2I2Y2M4OTkzMWQ0NjBhOTJlNDAyNTczNGM5NjhlNCJ9.YhLWtS5wyE2p7SYp8xN_BK3WUfWLQhNdIrdZLS7f9Mc"
            }
        )

        assert res.status_code == 400
        assert res.text == '{"detail":"refresh token expired"}'


    def test_failed_authenticate_by_revoked_refresh_token(self):

        res = client.post(
            "api/auth/v1/authenticate",
            cookies={
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJnZW5fZHQiOiIyMDI0LzA1LzI1LCAxMzozODoxMiIsImV4cF9kdCI6IjIwMjQvMDUvMjYsIDEzOjM4OjEyIiwiaWRlbnQiOiI1Zjc0MWYxNzBjODA0NTY0OGU3NjllNGZkNjNkYmE3ZSIsInVzZXJfaWRlbnQiOiJiN2I2Y2M4OTkzMWQ0NjBhOTJlNDAyNTczNGM5NjhlNCJ9.EZKAOi4Kp0mV3OJlBlclqdZ_YgPOhGfMfb2K-F9Zbbw"
            }
        )

        assert res.status_code == 400
        assert res.text == '{"detail":"revoked token"}'


    def test_failed_update_tokens_wothout_refresh_token(self):

        res = client.post(
            "api/auth/v1/update-tokens",
            cookies={}
        )

        assert res.status_code == 400
        assert res.text == '{"detail":"refresh token required"}'


    def test_failed_update_tokens_by_revoked_refresh_token(self):

        res = client.post(
            "api/auth/v1/update-tokens",
            cookies={
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJnZW5fZHQiOiIyMDI0LzA1LzI1LCAxMzozODoxMiIsImV4cF9kdCI6IjIwMjQvMDUvMjYsIDEzOjM4OjEyIiwiaWRlbnQiOiI1Zjc0MWYxNzBjODA0NTY0OGU3NjllNGZkNjNkYmE3ZSIsInVzZXJfaWRlbnQiOiJiN2I2Y2M4OTkzMWQ0NjBhOTJlNDAyNTczNGM5NjhlNCJ9.EZKAOi4Kp0mV3OJlBlclqdZ_YgPOhGfMfb2K-F9Zbbw"
            }
        )

        assert res.status_code == 400
        assert res.text == '{"detail":"revoked token"}'
        

    def test_failed_authorizate_by_invalid_login(self):
        res = client.post(
            "api/auth/v1/authorizate",
            json={
                "login": "SomeInvalidLogin",
                "password": "QWE123df"
            }
        )

        assert res.status_code == 400
        assert res.text == '{"detail":"user (SomeInvalidLogin) not found"}'


    def test_failed_authorizate_by_invalid_password(self):
        res = client.post(
            "api/auth/v1/authorizate",
            json={
                "login": "TestUser",
                "password": "QWE123df1111"
            }
        )

        assert res.status_code == 400
        assert res.text == '{"detail":"Invalid password"}'


    def test_authorizate(self):
        res = client.post(
            "api/auth/v1/authorizate",
            json={
                "login": "TestUser",
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
            "api/auth/v1/authenticate",
        )

        assert res.status_code == 200

        assert res.cookies.get("access_token") != access_token

    
    def test_update_token(self):
        refresh_token = copy(client.cookies["refresh_token"])

        res = client.post(
            "api/auth/v1/update-tokens",
        )

        assert res.status_code == 200

        assert res.cookies.get("refresh_token") != refresh_token


    def test_validate_access_token(self):

        res = client.post(
            "api/auth/v1/validate-access",
        )

        assert res.status_code == 200
