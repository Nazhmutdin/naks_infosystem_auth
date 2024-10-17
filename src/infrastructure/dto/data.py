from uuid import UUID
from typing import Annotated
from datetime import datetime, UTC

from pydantic.dataclasses import dataclass
from pydantic import BaseModel
from naks_library.utils.validators import plain_datetime_serializer


class LoginData(BaseModel):
    login: str
    password: str


@dataclass
class AccessTokenDTO:
    token: str
    user_ident: UUID
    gen_dt: datetime
    exp_dt: datetime


    @property
    def expired(self) -> bool:
        return datetime.now(UTC).replace(tzinfo=None) > self.exp_dt


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
