import typing as t
from uuid import UUID
from datetime import datetime
from hashlib import sha256

from jose.jwt import encode as jwt_encode, decode as jwt_decode, get_unverified_claims
from naks_library.funcs import to_uuid, str_to_datetime, is_uuid

from src.settings import Settings


class AccessTokenPayloadData(t.TypedDict):
    gen_dt: datetime
    user_ident: UUID | str


class RefreshTokenPayloadData(t.TypedDict):
    gen_dt: datetime
    exp_dt: datetime
    ident: UUID | str
    user_ident: UUID | str


class AuthService:
    def __init__(self, alg: str | list[str]="HS256", secret: str = Settings.SECRET_KEY()) -> None:
        self.algorithms = alg
        self.secret = secret


    def create_access_token(self, **payloads: t.Unpack[AccessTokenPayloadData]) -> str:

        if not payloads.get("gen_dt") or not isinstance(payloads.get("gen_dt"), datetime):
            raise ValueError("gen_dt is required")

        if not is_uuid(payloads.get("user_ident")):
            raise ValueError("invalid user_ident")
        
        payloads["gen_dt"] = payloads["gen_dt"].strftime("%Y/%m/%d, %H:%M:%S.%f")
        payloads["user_ident"] = to_uuid(payloads["user_ident"]).hex

        return jwt_encode(payloads, self.secret, algorithm=self.algorithms)


    def create_refresh_token(self, **payloads: t.Unpack[RefreshTokenPayloadData]):

        if not payloads.get("gen_dt") or not isinstance(payloads.get("gen_dt"), datetime):
            raise ValueError("gen_dt is required")

        if not payloads.get("exp_dt") or not isinstance(payloads.get("exp_dt"), datetime):
            raise ValueError("exp_dt is required")

        if not is_uuid(payloads.get("user_ident")):
            raise ValueError("invalid user_ident")
        
        payloads["gen_dt"] = payloads["gen_dt"].strftime("%Y/%m/%d, %H:%M:%S")
        payloads["exp_dt"] = payloads["exp_dt"].strftime("%Y/%m/%d, %H:%M:%S")
        payloads["user_ident"] = to_uuid(payloads["user_ident"]).hex
        payloads["ident"] = to_uuid(payloads["ident"]).hex

        return jwt_encode(payloads, self.secret, algorithm=self.algorithms)


    def read_token(self, token: str) -> dict[str, t.Any]:
        return jwt_decode(token, self.secret, algorithms=self.algorithms)
     

    def validate_access_token(self, token: str) -> bool: 
        payload = self._get_token_claims(token)
        
        if not payload:
            return False
        
        payload["gen_dt"] = str_to_datetime(payload["gen_dt"])

        return self.create_access_token(**payload) == token
    

    def validate_refresh_token(self, token: str) -> bool:
        payload = self._get_token_claims(token)

        if not payload:
            return False
        
        payload["gen_dt"] = str_to_datetime(payload["gen_dt"])
        payload["exp_dt"] = str_to_datetime(payload["exp_dt"])
        
        return self.create_refresh_token(**payload) == token
    

    def _get_token_claims(self, token: str) -> dict | None:
        try:
            return get_unverified_claims(token)
        except:
            return None
        

    def hash_password(self, password: str) -> str:
        return sha256(password.encode()).hexdigest()


    def validate_password(self, password: str, hashed_password: str) -> bool:
        return sha256(password.encode()).hexdigest() == hashed_password
