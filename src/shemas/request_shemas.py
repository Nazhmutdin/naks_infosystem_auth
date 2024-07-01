from datetime import datetime, date
from uuid import UUID
import typing as t

from naks_library.base_request_shema import *
from naks_library import to_datetime, is_uuid
from pydantic import Field, field_validator

from src.utils.funcs import validate_refresh_token
from src.models import *


__all__ = [
    "RefreshTokenRequestShema"
]


class RefreshTokenRequestShema(BaseRequestShema):
    __and_model_columns__ = ["exp_dt", "gen_dt", "revoked"]
    __or_model_columns__ = ["token", "user_ident", "ident"]
    __models__ = [RefreshTokenModel]

    tokens: InFilter | None = Field(default=None, serialization_alias="token")
    idents: InFilter | None = Field(default=None, serialization_alias="ident")
    user_idents: InFilter | None = Field(default=None, serialization_alias="user_ident", validation_alias="userIdents")
    revoked: EqualFilter | None = Field(default=None, serialization_alias="revoked")
    gen_dt_from: FromFilter | None = Field(default=None, serialization_alias="gen_dt", validation_alias="genDtFrom")
    gen_dt_before: BeforeFilter | None = Field(default=None, serialization_alias="gen_dt", validation_alias="genDtBefore")
    exp_dt_from: FromFilter | None = Field(default=None, serialization_alias="exp_dt", validation_alias="expDtFrom")
    exp_dt_before: BeforeFilter | None = Field(default=None, serialization_alias="exp_dt", validation_alias="expDtBefore")


    @field_validator("exp_dt_from", "exp_dt_before", "gen_dt_from", "gen_dt_before", mode="before")
    @classmethod
    def validate_datetime_filters(cls, v: datetime | date | str | None):
        if v == None:
            return None
        
        if isinstance(v, (datetime, date)):
            return v
        
        return to_datetime(v)
    

    @field_validator("idents", "user_idents", mode="before")
    @classmethod
    def validate_ident_filters(cls, v: list[UUID | str] | None):
        if v == None:
            return None
        
        if not isinstance(v, t.Iterable):
            raise ValueError(f"value must be iterable")
        
        for el in v:
            if not is_uuid(el):
                v.remove(el)
        
        if not v:
            return None
        
        return v
    

    @field_validator("tokens", mode="before")
    @classmethod
    def validate_tokens_filter(cls, v: list[str] | None):
        if v == None:
            return None
        
        if not isinstance(v, t.Iterable):
            raise ValueError(f"value must be iterable")
        
        for el in v:
            if not validate_refresh_token(el):
                print(el)
                v.remove(el)
        
        if not v:
            return None
        
        return v
    

    @field_validator("revoked", mode="before")
    @classmethod
    def validate_revoked_filter(cls, v: bool | None):
        if v == None:
            return None
        
        if not isinstance(v, bool):
            raise ValueError(f"revoked filter must be bool")
        
        return v
