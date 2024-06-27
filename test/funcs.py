import json

from shemas import *


def get_users() -> list[UserShema]:
    users = json.load(open("test/test_data/users.json", "r", encoding="utf-8"))
    return [UserShema.model_validate(user) for user in users]


def get_refresh_tokens() -> list[RefreshTokenShema]:
    tokens = json.load(open("test/test_data/refresh_tokens.json", "r", encoding="utf-8"))
    return [RefreshTokenShema.model_validate(token) for token in tokens]


def get_request_refresh_tokens() -> list[RefreshTokenShema]:
    tokens = json.load(open("test/test_data/request_refresh_tokens.json", "r", encoding="utf-8"))
    return tokens
