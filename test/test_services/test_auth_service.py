from datetime import datetime, timedelta

import pytest
from naks_library import str_to_datetime

from services.auth_service import AuthService

service = AuthService()


def test_create_access_token():
    token = service.create_access_token(gen_dt=datetime(2024, 1, 1, 1, 1, 1), user_ident="b7b6cc89931d460a92e4025734c968e4")

    assert token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJnZW5fZHQiOiIyMDI0LzAxLzAxLCAwMTowMTowMS4wMDAwMDAiLCJ1c2VyX2lkZW50IjoiYjdiNmNjODk5MzFkNDYwYTkyZTQwMjU3MzRjOTY4ZTQifQ.sfzvb0ge6Hr6Pt5hML3KHjj8bobmxmfg667nYzJQCPo"


@pytest.mark.parametrize(
        "payload",
        [
            {"gen_dt": "fsrefsd", "user_ident": "b7b6cc89931d460a92e4025734c968e4"},
            {"gen_dt": datetime.now() + timedelta(minutes=60), "user_ident": "fsfrrf"},
            {"gen_dt": "fsrefsd", "user_ident": "fsfrrf"}
        ]
)
def test_create_access_token_failed(payload: dict):
    with pytest.raises(ValueError):
        service.create_access_token(**payload)


def test_read_token():
    payload = {
        "gen_dt": datetime.now() + timedelta(minutes=60), 
        "user_ident": "b7b6cc89931d460a92e4025734c968e4"
    }
    token = service.create_access_token(
        gen_dt=datetime.now() + timedelta(minutes=60), 
        user_ident="b7b6cc89931d460a92e4025734c968e4"
    )

    token_data = service.read_token(token)

    token_data["gen_dt"] = str_to_datetime(token_data["gen_dt"])

    assert token_data == payload


def test_create_refresh_token():
    token = service.create_refresh_token(
        gen_dt=datetime(2024, 1, 1, 1, 1, 1), 
        exp_dt=datetime(2024, 1, 1, 1, 1, 1) + timedelta(minutes=60), 
        user_ident="b7b6cc89931d460a92e4025734c968e4",
        ident="b7c6cc89931d460a92e4025734c968e4"
    )

    assert token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJnZW5fZHQiOiIyMDI0LzAxLzAxLCAwMTowMTowMSIsImV4cF9kdCI6IjIwMjQvMDEvMDEsIDAyOjAxOjAxIiwidXNlcl9pZGVudCI6ImI3YjZjYzg5OTMxZDQ2MGE5MmU0MDI1NzM0Yzk2OGU0IiwiaWRlbnQiOiJiN2M2Y2M4OTkzMWQ0NjBhOTJlNDAyNTczNGM5NjhlNCJ9.yPBBou9VJuiitPSBJUANXleia-BXuR__AJ93a6Geq2Y"


@pytest.mark.parametrize(
        "payload",
        [
            {"gen_dt": "cdwss", "exp_dt": "fsrefsd", "user_ident": "b7b6cc89931d460a92e4025734c968e4"},
            {"gen_dt": "cdwss", "exp_dt": datetime.now() + timedelta(minutes=60), "user_ident": "fsfrrf"},
            {"gen_dt": datetime.now(), "exp_dt": "fssrfr", "user_ident": "fsfrrf"},
            {"gen_dt": "cdwss", "exp_dt": "fsrefsd", "user_ident": "fsfrrf"}
        ]
)
def test_create_refresh_token_failed(payload: dict):
    with pytest.raises(ValueError):
        service.create_refresh_token(**payload)


@pytest.mark.parametrize(
    "token",
    [
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJnZW5fZHQiOiIyMDI0LzA2LzA1LCAxMjoxMjozMC4wMDAwMDAiLCJ1c2VyX2lkZW50IjoiYjdiNmNjODk5MzFkNDYwYTkyZTQwMjU3MzRjOTY4ZTQifQ.wumHtxxWnqfWJFpUCK4gbchaTWT8jYZjSZlj586hEQk"
    ]
)
def test_validate_access_token(token: str):
    print(service.read_token(token))
    assert service.validate_access_token(token)

    
@pytest.mark.parametrize(
    "token",
    [
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJnZW5fZHQiOiIyMDI0LzA1LzI5LCAxMDo1mTowMiIsInVzZXJfaWRlbnQiOiJiN2I2Y2M4OTkzMWQ0NjBhOTJlNDAyNTczNGM5NjhlNCJ9.scwrMCIRTx-rhwqKFXX3Jjd8sN5vtBUD9Uc56C96dII"
    ]
)
def test_validate_access_token_invalid(token: str):
    assert not service.validate_access_token(token)


@pytest.mark.parametrize(
    "token",
    [
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJnZW5fZHQiOiIyMDI0LzA1LzI5LCAxMzozODoxMiIsImV4cF9kdCI6IjIwMjQvMDUvMzAsIDEzOjM4OjEyIiwidXNlcl9pZGVudCI6IjcyZTM4ZjYwYTAyNTQ5OWRiMjVjNzRhYWMwNGNhMTliIiwiaWRlbnQiOiIyZTQzMDQ4YWRiYmM0ZDVlYjZmMTlhMWMyODdlNGUwOCJ9.kvBSU70rKnzewF7MjQnnIIGAdkWn9ZWfMDCR1KVILyw"
    ]
)
def test_validate_refresh_token(token: str):
    assert service.validate_refresh_token(token)

    
@pytest.mark.parametrize(
    "token",
    [
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJnZW5fZHQiOiIyMDI0LzA1LzI5LCAxmzozODoxMiIsImV4cF9kdCI6IjIwMjQvMDUvMzAsIDEzOjM4OjEyIiwidXNlcl9pZGVudCI6IjcyZTM4ZjYwYTAyNTQ5OWRiMjVjNzRhYWMwNGNhMTliIiwiaWRlbnQiOiIyZTQzMDQ4YWRiYmM0ZDVlYjZmMTlhMWMyODdlNGUwOCJ9.kvBSU70rKnzewF7MjQnnIIGAdkWn9ZWfMDCR1KVILyw"
    ]
)
def test_validate_refresh_token_invalid(token: str):
    assert not service.validate_refresh_token(token)


def test_hash_password():
    string = "fsfrfrfrecawsd"

    assert service.hash_password(string) == "d41786f76466fc28a1750713d33ebbbdd781110140f131e4f40b687bc6955107"


def test_successful_password_validation():
    string = "hrtydfdgt"

    hashed = service.hash_password(string)

    assert service.validate_password(string, hashed)
    

def test_failed_password_validation():
    string = "hrtydfdgt"

    hashed = service.hash_password(string)

    assert not service.validate_password("fsrsdd", hashed)
