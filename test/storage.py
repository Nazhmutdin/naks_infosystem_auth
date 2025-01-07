from uuid import UUID, uuid4
from datetime import datetime, timedelta
from itertools import batched

from faker import Faker

from app.infrastructure.services.hasher import PasswordHasher
from app.infrastructure.services.jwt_service import JwtService
from app.application.dto import UserDTO, RefreshTokenDTO, PermissionDTO


PROJECTS = ["UST-LUGA", "MURMANSK", "AMUR"]


class IFakeDataGenerator:
    faker = Faker()


class FakeUserDataGenerator(IFakeDataGenerator):
    hasher = PasswordHasher()


    def generate_test_data(self, k: int = 3) -> list[dict]:
        res = []

        for i in range(k):
            sub_data = {}

            sub_data["ident"] = uuid4()
            sub_data["name"] = self.faker.name()
            sub_data["login"] = self._gen_login(sub_data["name"])
            sub_data["password"] = "QWE123df"
            sub_data["hashed_password"] = self.hasher.hash(sub_data["password"])
            sub_data["email"] = self.faker.email()
            sub_data["project"] = [self.faker.random_element(PROJECTS)]
            sub_data["sign_dt"] = self.faker.date_time()
            sub_data["update_dt"] = self.faker.date_time()
            sub_data["login_dt"] = self.faker.date_time()

            res.append(sub_data)
        
        return res
    

    def _gen_login(self, name: str) -> str:
        return name.replace(" ", "") + "".join(self.faker.random_choices([str(el) for el in range(9)], 5))


class FakeRefreshTokenDataGenerator(IFakeDataGenerator):
    auth_service = JwtService()


    def __init__(self, users: list[UserDTO]) -> None:
        self.users = users

    
    def generate_test_data(self, k: int = 15) -> list[dict]:
        data = []

        for _ in range(k):
            sub_data = {}

            sub_data["ident"] = uuid4()
            sub_data["revoked"] = self.faker.random_element([True, False, False])
            sub_data["exp_dt"] = self.faker.date_time_between_dates(
                datetime.now() - timedelta(hours=12),
                datetime.now() + timedelta(hours=12)
            ).replace(tzinfo=None)
            sub_data["gen_dt"] = sub_data["exp_dt"] - timedelta(days=1)

            data.append(sub_data)


        for user, refresh_datas in zip(self.users, batched(data, int(len(data) // len(self.users)))):
            for refresh_data in refresh_datas:
                refresh_data["user_ident"] = user.ident
                refresh_data["token"] = self.auth_service.create_refresh_token(
                    gen_dt=refresh_data["gen_dt"], 
                    exp_dt=refresh_data["exp_dt"], 
                    ident=refresh_data["ident"], 
                    user_ident=refresh_data["user_ident"]
                )


        return data


class FakePermissionDataGenerator(IFakeDataGenerator):

    def __init__(self, users: list[UserDTO]) -> None:
        self.users = users

    
    def generate_test_data(self) -> list[dict]:
        data = []

        data.append(self._generate(self.users[0], True))

        for user in self.users[1:]:
            data.append(self._generate(user, False))

        return data
    

    def _generate(self, user: UserDTO, is_super_user: bool) -> dict:
        sub_data = {}

        sub_data["ident"] = uuid4()
        sub_data["user_ident"] = user.ident

        sub_data["is_super_user"] = is_super_user

        sub_data["personal_data_get"] = self.faker.random_element([True, False])
        sub_data["personal_data_create"] = self.faker.random_element([True, False])
        sub_data["personal_data_update"] = self.faker.random_element([True, False])
        sub_data["personal_data_delete"] = self.faker.random_element([True, False])

        sub_data["personal_naks_certification_data_get"] = self.faker.random_element([True, False])
        sub_data["personal_naks_certification_data_create"] = self.faker.random_element([True, False])
        sub_data["personal_naks_certification_data_update"] = self.faker.random_element([True, False])
        sub_data["personal_naks_certification_data_delete"] = self.faker.random_element([True, False])

        sub_data["ndt_data_get"] = self.faker.random_element([True, False])
        sub_data["ndt_data_create"] = self.faker.random_element([True, False])
        sub_data["ndt_data_update"] = self.faker.random_element([True, False])
        sub_data["ndt_data_delete"] = self.faker.random_element([True, False])

        sub_data["acst_data_get"] = self.faker.random_element([True, False])
        sub_data["acst_data_create"] = self.faker.random_element([True, False])
        sub_data["acst_data_update"] = self.faker.random_element([True, False])
        sub_data["acst_data_delete"] = self.faker.random_element([True, False])

        sub_data["acst_file_download"] = self.faker.random_element([True, False])
        sub_data["acst_file_upload"] = self.faker.random_element([True, False])

        sub_data["personal_naks_certification_file_download"] = self.faker.random_element([True, False])
        sub_data["personal_naks_certification_file_upload"] = self.faker.random_element([True, False])

        sub_data["personal_naks_protocol_file_download"] = self.faker.random_element([True, False])
        sub_data["personal_naks_protocol_file_upload"] = self.faker.random_element([True, False])

        return sub_data
    

class StorageTestData:
    def __init__(self) -> None:
        self.fake_user_generator = FakeUserDataGenerator()
        self.fake_users_dicts = self.fake_user_generator.generate_test_data()
        self.fake_users = [self._to_user_dto(el) for el in self.fake_users_dicts]

        self.fake_refresh_token_generator = FakeRefreshTokenDataGenerator(self.fake_users)
        self.fake_refresh_tokens_dicts = self.fake_refresh_token_generator.generate_test_data()
        self.fake_refresh_tokens = [self._to_refresh_token_dto(el) for el in self.fake_refresh_tokens_dicts]

        self.fake_pemissions_generator = FakePermissionDataGenerator(self.fake_users)
        self.fake_pemissions_dicts = self.fake_pemissions_generator.generate_test_data()
        self.fake_permissions = [self._to_permission_dto(el) for el in self.fake_pemissions_dicts]

    
    def _to_user_dto(self, data: dict) -> UserDTO:
        return UserDTO(**data)

    
    def _to_refresh_token_dto(self, data: dict) -> RefreshTokenDTO:
        return RefreshTokenDTO(
            ident=data["ident"],
            user_ident=data["user_ident"],
            token=data["token"],
            revoked=data["revoked"],
            gen_dt=data["gen_dt"],
            exp_dt=data["exp_dt"]
        ) 

    
    def _to_permission_dto(self, data: dict) -> PermissionDTO:
        return PermissionDTO(
            ident=data["ident"],
            user_ident=data["user_ident"],
            is_super_user=data["is_super_user"],
            personal_data_get = data["personal_data_get"],
            personal_data_create = data["personal_data_create"],
            personal_data_update = data["personal_data_update"],
            personal_data_delete = data["personal_data_delete"],
            personal_naks_certification_data_get = data["personal_naks_certification_data_get"],
            personal_naks_certification_data_create = data["personal_naks_certification_data_create"],
            personal_naks_certification_data_update = data["personal_naks_certification_data_update"],
            personal_naks_certification_data_delete = data["personal_naks_certification_data_delete"],
            ndt_data_get = data["ndt_data_get"],
            ndt_data_create = data["ndt_data_create"],
            ndt_data_update = data["ndt_data_update"],
            ndt_data_delete = data["ndt_data_delete"],
            acst_data_get = data["acst_data_get"],
            acst_data_create = data["acst_data_create"],
            acst_data_update = data["acst_data_update"],
            acst_data_delete = data["acst_data_delete"],
            acst_file_download = data["acst_file_download"],
            acst_file_upload = data["acst_file_upload"],
            personal_naks_certification_file_download = data["personal_naks_certification_file_download"],
            personal_naks_certification_file_upload = data["personal_naks_certification_file_upload"],
            personal_naks_protocol_file_download = data["personal_naks_protocol_file_download"],
            personal_naks_protocol_file_upload = data["personal_naks_protocol_file_upload"]
        ) 


    def get_expired_refresh_tokens(self) -> list[RefreshTokenDTO]:
        result = []

        for refresh_token in self.fake_refresh_tokens:
            if refresh_token.expired and not refresh_token.revoked:
                result.append(refresh_token)

        return result


    def get_revoked_refresh_tokens(self) -> list[RefreshTokenDTO]:
        result = []

        for refresh_token in self.fake_refresh_tokens:
            if refresh_token.revoked:
                result.append(refresh_token)

        return result


    def get_actual_refresh_token(self) -> RefreshTokenDTO:

        for refresh_token in self.fake_refresh_tokens:
            if not refresh_token.expired and not refresh_token.revoked:
                return refresh_token


    def get_actual_usual_user_refresh_token(self) -> RefreshTokenDTO:
        super_user = self.get_fake_superuser()

        for refresh_token in self.fake_refresh_tokens:
            if not refresh_token.expired and not refresh_token.revoked and (refresh_token.user_ident != super_user.ident):
                return refresh_token


    def get_actual_refresh_tokens(self) -> list[RefreshTokenDTO]:
        result = []

        for refresh_token in self.fake_refresh_tokens:
            if not refresh_token.expired and not refresh_token.revoked:
                result.append(refresh_token)

        return result


    def get_actual_superuser_refresh_token(self) -> RefreshTokenDTO:
        super_user = self.get_fake_superuser()

        for refresh_token in self.fake_refresh_tokens:
            if (not refresh_token.revoked) and (not refresh_token.expired) and (refresh_token.user_ident == super_user.ident):
                return refresh_token


    def get_fake_user(self, refresh_token: RefreshTokenDTO) -> UserDTO:
        for user in self.fake_users:
            if refresh_token.user_ident == user.ident:
                return user
            
    
    def get_fake_superuser(self) -> UserDTO:
        return self.fake_users[0]
            
    
    def get_fake_superuser_dict(self) -> dict:
        return self.fake_users_dicts[0]
                    

    def get_user_permission(self, user_ident: UUID) -> PermissionDTO:
        for permission in self.fake_permissions:
            if user_ident == permission.user_ident:
                return permission


storage = StorageTestData()