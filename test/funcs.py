import json
from uuid import uuid4
from datetime import datetime, timedelta

from faker import Faker

from shemas import *
from services.auth_service import AuthService
from utils.DTOs import UserData, RefreshTokenData


class IFakeDataGenerator:
    faker = Faker()

    def generate(self, k: int = 15) -> list[dict]:
        ...


class FakeUserDataGenerator(IFakeDataGenerator):
    auth_service = AuthService()

    def generate(self, k: int = 10) -> list[dict]:
        data = []

        for _ in range(k):
            sub_data = {}

            sub_data["ident"] = uuid4()
            sub_data["name"] = self.faker.name()
            sub_data["login"] = self.gen_login(sub_data["name"])
            sub_data["password"] = self.faker.password(8)
            sub_data["hashed_password"] = self.auth_service.hash_password(sub_data["password"])
            sub_data["email"] = self.faker.email()
            sub_data["sign_dt"] = self.faker.date_time()
            sub_data["update_dt"] = self.faker.date_time()
            sub_data["login_dt"] = self.faker.date_time()
            sub_data["is_superuser"] = False

            data.append(sub_data)
        
        
        sub_data = {}

        sub_data["ident"] = uuid4()
        sub_data["name"] = self.faker.name()
        sub_data["login"] = self.gen_login(sub_data["name"])
        sub_data["password"] = self.faker.password(8)
        sub_data["hashed_password"] = self.auth_service.hash_password(sub_data["password"])
        sub_data["email"] = self.faker.email()
        sub_data["sign_dt"] = self.faker.date_time()
        sub_data["update_dt"] = self.faker.date_time()
        sub_data["login_dt"] = self.faker.date_time()
        sub_data["is_superuser"] = True

        data.append(sub_data)
        
        return data


    def gen_login(self, name: str):
        result = name.replace(" ", "") + "".join([str(el) for el in self.faker.random_choices(range(10), 5)])

        return result


class FakeRefreshTokenDataGenerator(IFakeDataGenerator):
    auth_service = AuthService()

    def __init__(self, users: list[UserData]) -> None:
        self.users = users

    
    def generate(self, k: int = 25) -> list[dict]:
        data = []

        for _ in range(k):
            sub_data = {}

            sub_data["ident"] = uuid4()
            sub_data["user_ident"] = self.faker.random_element(self.users).ident
            sub_data["revoked"] = self.faker.random_element([True, False, False])
            sub_data["exp_dt"] = self.faker.date_time_between_dates(
                datetime.now() - timedelta(hours=12),
                datetime.now() + timedelta(hours=12)
            ).replace(tzinfo=None)
            sub_data["gen_dt"] = sub_data["exp_dt"] - timedelta(days=1)
            sub_data["token"] = self.auth_service.create_refresh_token(
                gen_dt=sub_data["gen_dt"], 
                exp_dt=sub_data["exp_dt"], 
                ident=sub_data["ident"], 
                user_ident=sub_data["user_ident"]
            )

            data.append(sub_data)

        sub_data = {}

        sub_data["ident"] = uuid4()
        sub_data["user_ident"] = self.get_superuser().ident
        sub_data["revoked"] = False
        sub_data["exp_dt"] = (datetime.now() + timedelta(hours=12)).replace(tzinfo=None)
        sub_data["gen_dt"] = (sub_data["exp_dt"] - timedelta(days=1)).replace(tzinfo=None)
        sub_data["token"] = self.auth_service.create_refresh_token(
            gen_dt=sub_data["gen_dt"], 
            exp_dt=sub_data["exp_dt"], 
            ident=sub_data["ident"], 
            user_ident=sub_data["user_ident"]
        )

        data.append(sub_data)
        
        return data
    

    def get_superuser(self) -> UserData:
        for user in self.users:
            if user.is_superuser:
                return user
    

class TestData:
    def __init__(self) -> None:
        self.fake_user_generator = FakeUserDataGenerator()
        self.fake_users_dicts = self.fake_user_generator.generate()
        self.fake_refresh_token_generator = FakeRefreshTokenDataGenerator(self.fake_users)
        self.fake_refresh_tokens_dicts = self.fake_refresh_token_generator.generate()

    @property
    def fake_users(self) -> list[UserData]:
        return [UserData(**el) for el in self.fake_users_dicts]


    @property
    def fake_refresh_tokens(self) -> list[RefreshTokenData]:
        return [RefreshTokenData(**el) for el in self.fake_refresh_tokens_dicts]
    
    
    def get_expired_refresh_tokens(self) -> list[RefreshTokenData]:
        result = []

        for refresh_token in test_data.fake_refresh_tokens:
            if refresh_token.expired and not refresh_token.revoked:
                result.append(refresh_token)

        return result


    def get_revoked_refresh_tokens(self) -> list[RefreshTokenData]:
        result = []

        for refresh_token in test_data.fake_refresh_tokens:
            if refresh_token.revoked:
                result.append(refresh_token)

        return result


    def get_actual_refresh_tokens(self) -> list[RefreshTokenData]:
        result = []

        for refresh_token in test_data.fake_refresh_tokens:
            if not refresh_token.expired and not refresh_token.revoked:
                result.append(refresh_token)

        return result


    def get_actual_superuser_refresh_token(self) -> RefreshTokenData:
        for refresh_token in test_data.fake_refresh_tokens:
            if not refresh_token.revoked and not refresh_token.expired and self.get_fake_user(refresh_token).is_superuser:
                return refresh_token


    def get_fake_user(self, refresh_token: RefreshTokenData) -> UserData:
        for user in test_data.fake_users:
            if refresh_token.user_ident == user.ident:
                return user


test_data = TestData()


def get_request_refresh_tokens() -> list[RefreshTokenShema]:
    tokens = json.load(open("test/test_data/request_refresh_tokens.json", "r", encoding="utf-8"))
    return tokens
