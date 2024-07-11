import typing as t
from datetime import datetime, timedelta, UTC

from naks_library import BaseShema, str_to_datetime

from src.services.auth_service import AuthService, AccessTokenPayloadData


class AccessTokenShema(BaseShema):
    token: str
    gen_dt: datetime
    exp_dt: datetime


    @classmethod
    def from_token(cls, token: str) -> t.Self:
        payload: AccessTokenPayloadData = AuthService().read_token(token)

        gen_dt = str_to_datetime(payload["gen_dt"])

        return cls(
            token=token,
            gen_dt=gen_dt,
            exp_dt=gen_dt + timedelta(minutes=60)
        )


    @property
    def is_expired(self) -> bool:
        return datetime.now(UTC).replace(tzinfo=None) > self.exp_dt
