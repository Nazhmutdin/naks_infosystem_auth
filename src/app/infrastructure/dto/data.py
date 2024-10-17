from uuid import UUID
from datetime import datetime, UTC

from pydantic.dataclasses import dataclass
from pydantic import BaseModel


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