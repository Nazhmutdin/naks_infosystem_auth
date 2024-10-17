from uuid import uuid4
from datetime import datetime, timedelta

from faker import Faker

from infrastructure.services.hasher import PasswordHasher
from infrastructure.services.jwt_service import JwtService
from infrastructure.dto import RefreshTokenDTO
from application.dto import UserDTO



class IFakeDataGenerator:
    faker = Faker()

    def generate(self, k: int = 15) -> list[dict]:
        ...


class FakeUserDataGenerator(IFakeDataGenerator):
    hasher = PasswordHasher()

    def generate(self, k: int = 10) -> list[dict]:
        data = []

        for _ in range(k):
            sub_data = {}

            sub_data["ident"] = uuid4()
            sub_data["name"] = self.faker.name()
            sub_data["login"] = self.gen_login(sub_data["name"])
            sub_data["password"] = self.faker.password(8)
            sub_data["hashed_password"] = self.hasher.hash(sub_data["password"])
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
        sub_data["hashed_password"] = self.hasher.hash(sub_data["password"])
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
    auth_service = JwtService()

    def __init__(self, users: list[UserDTO]) -> None:
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
    

    def get_superuser(self) -> UserDTO:
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
    def fake_users(self) -> list[UserDTO]:
        return [UserDTO(**el) for el in self.fake_users_dicts]


    @property
    def fake_refresh_tokens(self) -> list[RefreshTokenDTO]:
        return [RefreshTokenDTO(**el) for el in self.fake_refresh_tokens_dicts]
    
    
    def get_expired_refresh_tokens(self) -> list[RefreshTokenDTO]:
        result = []

        for refresh_token in test_data.fake_refresh_tokens:
            if refresh_token.expired and not refresh_token.revoked:
                result.append(refresh_token)

        return result


    def get_revoked_refresh_tokens(self) -> list[RefreshTokenDTO]:
        result = []

        for refresh_token in test_data.fake_refresh_tokens:
            if refresh_token.revoked:
                result.append(refresh_token)

        return result


    def get_actual_refresh_token(self) -> RefreshTokenDTO:

        for refresh_token in self.fake_refresh_tokens:
            if not refresh_token.expired and not refresh_token.revoked and not self.get_fake_user(refresh_token).is_superuser:
                return refresh_token


    def get_actual_refresh_tokens(self) -> list[RefreshTokenDTO]:
        result = []

        for refresh_token in test_data.fake_refresh_tokens:
            if not refresh_token.expired and not refresh_token.revoked:
                result.append(refresh_token)

        return result


    def get_actual_superuser_refresh_token(self) -> RefreshTokenDTO:
        for refresh_token in test_data.fake_refresh_tokens:
            if not refresh_token.revoked and not refresh_token.expired and self.get_fake_user(refresh_token).is_superuser:
                return refresh_token


    def get_fake_user(self, refresh_token: RefreshTokenDTO) -> UserDTO:
        for user in test_data.fake_users:
            if refresh_token.user_ident == user.ident:
                return user


test_data = TestData()
