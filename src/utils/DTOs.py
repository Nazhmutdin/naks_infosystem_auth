from uuid import UUID
from datetime import datetime, timedelta
from typing import Annotated

from pydantic.dataclasses import dataclass
from naks_library import Eq
from naks_library.validators import before_datetime_validator

from src.utils.funcs import current_utc_datetime_without_timezone
from src.settings import Settings

__all__ = [
    "UserData",
    "RefreshTokenData"
]


@dataclass(eq=False)
class UserData(Eq):
    ident: UUID
    name: str
    login: str
    hashed_password: str
    email: str | None
    sign_dt: Annotated[datetime, before_datetime_validator]
    update_dt: Annotated[datetime, before_datetime_validator]
    login_dt: Annotated[datetime, before_datetime_validator]
    is_superuser: bool


@dataclass(eq=False)
class RefreshTokenData(Eq):
    ident: UUID
    user_ident: UUID 
    token: str
    revoked: bool
    exp_dt: Annotated[datetime, before_datetime_validator]
    gen_dt: Annotated[datetime, before_datetime_validator]

    @property
    def expired(self) -> bool:
        return current_utc_datetime_without_timezone() > self.exp_dt


@dataclass(eq=False)
class AccessTokenData(Eq):
    gen_dt: Annotated[datetime, before_datetime_validator]
    user_ident: UUID
    token: str


    @property
    def exp_dt(self) -> datetime:
        return self.gen_dt + timedelta(minutes=Settings.ACCESS_TOKEN_LIFETIME_MINUTES())
