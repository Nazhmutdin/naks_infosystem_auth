from typing import Annotated
from datetime import datetime, UTC
from uuid import UUID

from pydantic.dataclasses import dataclass
from pydantic import EmailStr
from naks_library.utils.validators import plain_datetime_serializer


@dataclass
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


@dataclass
class CreateUserDTO(UserDTO): ...


@dataclass
class UpdateUserDTO:
    name: str | None
    login: str | None
    email: EmailStr | None
    sign_dt: datetime | None
    update_dt: datetime | None
    login_dt: datetime | None
    is_superuser: bool | None


type CurrentUser = UserDTO


@dataclass
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


@dataclass
class CreateRefreshTokenDTO(RefreshTokenDTO): ...


@dataclass
class UpdateRefreshTokenDTO:
    user_ident: UUID | None
    token: str | None
    revoked: bool | None
    gen_dt: datetime | None 
    exp_dt: datetime | None


def convert_create_refresh_token_dto_to_refresh_token_dto(dto: CreateRefreshTokenDTO) -> RefreshTokenDTO:
    return RefreshTokenDTO(
        ident=dto.ident,
        user_ident=dto.user_ident,
        token=dto.token,
        revoked=dto.revoked,
        gen_dt=dto.gen_dt,
        exp_dt=dto.exp_dt
    )


def convert_refresh_token_dto_to_create_refresh_token_dto(dto: RefreshTokenDTO) -> CreateRefreshTokenDTO:
    return RefreshTokenDTO(
        ident=dto.ident,
        user_ident=dto.user_ident,
        token=dto.token,
        revoked=dto.revoked,
        gen_dt=dto.gen_dt,
        exp_dt=dto.exp_dt
    )
