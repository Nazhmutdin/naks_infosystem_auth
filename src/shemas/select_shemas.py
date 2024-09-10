from datetime import datetime
from uuid import UUID
import typing as t

from naks_library.validators import before_optional_datetime_validator
from pydantic import Field, field_validator

from src.utils.funcs import validate_refresh_token
from src.models import *


__all__ = [
    "RefreshTokenSelectShema"
]


class RefreshTokenSelectShema:

    tokens: list[str] | None = Field(default=None)
    idents: list[UUID] | None = Field(default=None)
    user_idents: list[UUID] | None = Field(default=None, validation_alias="userIdents")
    revoked: bool | None = Field(default=None)
    gen_dt_from: t.Annotated[datetime | None, before_optional_datetime_validator] = Field(default=None, validation_alias="genDtFrom")
    gen_dt_before: t.Annotated[datetime | None, before_optional_datetime_validator] = Field(default=None, validation_alias="genDtBefore")
    exp_dt_from: t.Annotated[datetime | None, before_optional_datetime_validator] = Field(default=None, validation_alias="expDtFrom")
    exp_dt_before: t.Annotated[datetime | None, before_optional_datetime_validator] = Field(default=None, validation_alias="expDtBefore")
    

    @field_validator("tokens", mode="before")
    @classmethod
    def validate_tokens_filter(cls, v: list[str] | None):
        if v == None:
            return None
        
        if not isinstance(v, t.Iterable):
            raise ValueError(f"value must be iterable")
        
        for el in v:
            if not validate_refresh_token(el):
                v.remove(el)
        
        if not v:
            return None
        
        return v
