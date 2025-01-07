from typing import Annotated
from datetime import datetime, UTC
from uuid import UUID

from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, EmailStr
from naks_library.utils.validators import plain_datetime_serializer
from naks_library.common.root import camel_case_alias_generator


@dataclass(config=ConfigDict(alias_generator=camel_case_alias_generator, populate_by_name=True))
class UserDTO:
    ident: UUID
    login: str
    name: str
    email: EmailStr | None
    projects: list[str] | None
    hashed_password: str
    sign_dt: Annotated[datetime, plain_datetime_serializer]
    update_dt: Annotated[datetime, plain_datetime_serializer]
    login_dt: Annotated[datetime, plain_datetime_serializer]


@dataclass(config=ConfigDict(alias_generator=camel_case_alias_generator, populate_by_name=True))
class CreateUserDTO(UserDTO): ...


@dataclass(config=ConfigDict(alias_generator=camel_case_alias_generator, populate_by_name=True))
class UpdateUserDTO:
    name: str | None
    login: str | None
    email: EmailStr | None
    projects: list[str] | None
    sign_dt: datetime | None
    update_dt: datetime | None
    login_dt: datetime | None


type CurrentUser = UserDTO


@dataclass(config=ConfigDict(alias_generator=camel_case_alias_generator, populate_by_name=True))
class RefreshTokenDTO:
    ident: UUID
    user_ident: UUID
    token: str
    revoked: bool
    gen_dt: Annotated[datetime, plain_datetime_serializer] 
    exp_dt: Annotated[datetime, plain_datetime_serializer]

    @property
    def expired(self) -> bool:
        return datetime.now(UTC).replace(tzinfo=None) > self.exp_dt


@dataclass(config=ConfigDict(alias_generator=camel_case_alias_generator, populate_by_name=True))
class CreateRefreshTokenDTO(RefreshTokenDTO): ...


@dataclass(config=ConfigDict(alias_generator=camel_case_alias_generator, populate_by_name=True))
class UpdateRefreshTokenDTO:
    user_ident: UUID | None
    token: str | None
    revoked: bool | None
    gen_dt: datetime | None 
    exp_dt: datetime | None



@dataclass(config=ConfigDict(alias_generator=camel_case_alias_generator, populate_by_name=True))
class PermissionDTO:
    ident: UUID
    user_ident: UUID

    is_super_user: bool

    personal_data_get: bool
    personal_data_create: bool
    personal_data_update: bool
    personal_data_delete: bool

    personal_naks_certification_data_get: bool
    personal_naks_certification_data_create: bool
    personal_naks_certification_data_update: bool
    personal_naks_certification_data_delete: bool

    ndt_data_get: bool
    ndt_data_create: bool
    ndt_data_update: bool
    ndt_data_delete: bool

    acst_data_get: bool
    acst_data_create: bool
    acst_data_update: bool
    acst_data_delete: bool

    acst_file_download: bool
    acst_file_upload: bool

    personal_naks_certification_file_download: bool
    personal_naks_certification_file_upload: bool

    personal_naks_protocol_file_download: bool
    personal_naks_protocol_file_upload: bool


@dataclass(config=ConfigDict(alias_generator=camel_case_alias_generator, populate_by_name=True))
class CreatePermissionDTO(PermissionDTO): ...


@dataclass(config=ConfigDict(alias_generator=camel_case_alias_generator, populate_by_name=True))
class UpdatePermissionDTO:

    personal_data_get: bool | None
    personal_data_create: bool | None
    personal_data_update: bool | None
    personal_data_delete: bool | None

    personal_naks_certification_data_get: bool | None
    personal_naks_certification_data_create: bool | None
    personal_naks_certification_data_update: bool | None
    personal_naks_certification_data_delete: bool | None

    ndt_data_get: bool | None
    ndt_data_create: bool | None
    ndt_data_update: bool | None
    ndt_data_delete: bool | None

    acst_data_get: bool | None
    acst_data_create: bool | None
    acst_data_update: bool | None
    acst_data_delete: bool | None

    acst_file_download: bool | None
    acst_file_upload: bool | None

    personal_naks_certification_file_download: bool | None
    personal_naks_certification_file_upload: bool | None

    personal_naks_protocol_file_download: bool | None
    personal_naks_protocol_file_upload: bool | None


type CurrentUserPermission = PermissionDTO
