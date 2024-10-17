from typing import Any, TypedDict, Unpack
from uuid import UUID
from datetime import datetime
from copy import copy

from jose.jwt import encode as jwt_encode, decode as jwt_decode

from src.configs import ApplicationConfig


class AccessTokenPayload(TypedDict):
    user_ident: UUID
    gen_dt: datetime
    exp_dt: datetime


class RefreshTokenPayload(TypedDict):
    ident: UUID
    user_ident: UUID
    gen_dt: datetime
    exp_dt: datetime


class JwtService:
    def __init__(self) -> None:
        self.algorithm = ApplicationConfig.ALGORITHM()
        self.secret_key = ApplicationConfig.SECRET_KEY()

    
    def encode(
        self,
        payload: dict[str, Any]
    ) -> str:
        
        payload = copy(payload)

        payload["gen_dt"] = payload.pop("gen_dt").strftime("%d.%m.%Y %H:%M:%S.%f")
        payload["exp_dt"] = payload.pop("exp_dt").strftime("%d.%m.%Y %H:%M:%S.%f")

        return jwt_encode(
            payload,
            self.secret_key,
            self.algorithm
        )
    

    def decode(
        self,
        token: str
    ) -> dict[str, Any]:
        return jwt_decode(
            token,
            self.secret_key,
            self.algorithm
        )
    

    def create_access_token(
        self, 
        **payload: Unpack[AccessTokenPayload]
    ) -> str:
        
        payload["user_ident"] = payload["user_ident"].hex
        
        return self.encode(
            payload=payload
        )


    def create_refresh_token(
        self,
        **payload: Unpack[RefreshTokenPayload]
    ) -> str:
        payload["user_ident"] = payload["user_ident"].hex
        payload["ident"] = payload["ident"].hex
        
        return self.encode(
            payload=payload
        )
    

    def read_access_token(
        self,
        token: str
    ) -> AccessTokenPayload:
        data = self.decode(token)

        return AccessTokenPayload(
            user_ident=data["user_ident"],
            gen_dt=datetime.strptime(data["gen_dt"], "%d.%m.%Y %H:%M:%S.%f"),
            exp_dt=datetime.strptime(data["exp_dt"], "%d.%m.%Y %H:%M:%S.%f"),
        )
    

    def read_refresh_token(
        self,
        token: str
    ) -> RefreshTokenPayload:
        data = self.decode(token)

        return RefreshTokenPayload(
            ident=data["ident"],
            user_ident=data["user_ident"],
            gen_dt=datetime.strptime(data["gen_dt"], "%d.%m.%Y %H:%M:%S.%f"),
            exp_dt=datetime.strptime(data["exp_dt"], "%d.%m.%Y %H:%M:%S.%f"),
        )
