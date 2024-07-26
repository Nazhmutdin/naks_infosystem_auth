from uuid import UUID
from datetime import datetime, UTC

from pydantic.dataclasses import dataclass

from src.utils.funcs import current_utc_datetime_without_timezone

__all__ = [
    "UserData",
    "RefreshTokenData"
]


@dataclass
class UserData:
    ident: UUID
    name: str
    login: str
    hashed_password: str
    email: str | None
    sign_dt: datetime
    update_dt: datetime
    login_dt: datetime
    is_superuser: bool


@dataclass
class RefreshTokenData:
    ident: UUID
    user_ident: UUID 
    token: str
    revoked: bool
    exp_dt: datetime
    gen_dt: datetime

    @property
    def expired(self) -> bool:
        return current_utc_datetime_without_timezone() > self.exp_dt
