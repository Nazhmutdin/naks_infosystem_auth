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
    hashed_password: str
    sign_dt: Annotated[datetime, plain_datetime_serializer] 
    update_dt: Annotated[datetime, plain_datetime_serializer] 
    login_dt: Annotated[datetime, plain_datetime_serializer] 
    is_superuser: bool


@dataclass(config=ConfigDict(alias_generator=camel_case_alias_generator, populate_by_name=True))
class CreateUserDTO(UserDTO): ...


@dataclass(config=ConfigDict(alias_generator=camel_case_alias_generator, populate_by_name=True))
class UpdateUserDTO:
    name: str | None
    login: str | None
    email: EmailStr | None
    sign_dt: datetime | None
    update_dt: datetime | None
    login_dt: datetime | None
    is_superuser: bool | None


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