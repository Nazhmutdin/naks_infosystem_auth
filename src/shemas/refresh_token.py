from typing import Any
from uuid import UUID, uuid4
from datetime import datetime, UTC

from pydantic import Field, field_validator, computed_field
from naks_library import BaseShema, to_datetime

from src.utils.funcs import refresh_token_expiration_dt_without_timezone, current_utc_datetime_without_timezone, validate_refresh_token


class BaseRefreshTokenShema(BaseShema):
    __fields_ignore__ = ["ident"]
    
    user_ident: UUID | None = Field(default=None)
    token: str | None = Field(default=None)
    revoked: bool | None = Field(default=None)
    exp_dt: datetime | None = Field(default=None)
    gen_dt: datetime | None = Field(default=None)
        

    @field_validator("exp_dt", "gen_dt", mode="before")
    @classmethod
    def validate_datetimes(cls, v: str | datetime | None):
        if v == None:
            return v
        
        return to_datetime(v)
        

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str | None):
        if v == None:
            return None
        
        if validate_refresh_token(v):
            return v
        
        raise ValueError("invalid token")


class RefreshTokenShema(BaseRefreshTokenShema):
    ident: UUID
    user_ident: UUID
    token: str
    revoked: bool = Field(default=False)
    gen_dt: datetime = Field(default_factory=current_utc_datetime_without_timezone)
    exp_dt: datetime = Field(default_factory=refresh_token_expiration_dt_without_timezone)


    @field_validator("token")
    def validate_token(cls, v: str | None) -> str:
        if v == None:
            raise ValueError("token cannot be None")
        
        if validate_refresh_token(v):
            return v
        else:
            raise ValueError(f"invalid token {v}")


    @field_validator("exp_dt", "gen_dt", mode="before")
    @classmethod
    def validate_datetimes(cls, v: str | datetime | None):
        
        return to_datetime(v)


    @computed_field
    @property
    def expired(self) -> bool:
        return datetime.now(UTC).replace(tzinfo=None) > self.exp_dt
            

class CreateRefreshTokenShema(RefreshTokenShema):
    ident: UUID = Field(default_factory=uuid4)

    def model_dump(self, *, mode: str = 'python', include: set[int] | set[str] | dict[int, Any] | dict[str, Any] | None = None, exclude: set[int] | set[str] | dict[int, Any] | dict[str, Any] | None = None, by_alias: bool = False, exclude_unset: bool = False, exclude_defaults: bool = False, exclude_none: bool = False, round_trip: bool = False, warnings: bool = True) -> dict[str, Any]:
        data = super().model_dump(mode=mode, include=include, exclude=exclude, by_alias=by_alias, exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, exclude_none=exclude_none, round_trip=round_trip, warnings=warnings)

        del data["expired"]

        return data


class UpdateRefreshTokenShema(BaseRefreshTokenShema): ...
