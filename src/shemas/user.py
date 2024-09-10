from uuid import UUID, uuid4
from datetime import datetime
import typing as t

from pydantic import ValidationInfo, EmailStr, Field, field_validator, model_validator
from naks_library import BaseShema, to_datetime
from naks_library.validators import before_optional_datetime_validator, before_datetime_validator

from src.services.auth_service import AuthService


class BaseUserShema(BaseShema):
    __fields_ignore__ = ["ident"]
    
    name: str | None = Field(default=None) 
    login: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    sign_dt: t.Annotated[datetime | None, before_optional_datetime_validator] = Field(default=None)
    update_dt: t.Annotated[datetime | None, before_optional_datetime_validator] = Field(default=None)
    login_dt: t.Annotated[datetime | None, before_optional_datetime_validator] = Field(default=None)


class UserShema(BaseUserShema):
    ident: UUID
    login: str
    name: str
    hashed_password: str
    sign_dt: t.Annotated[datetime, before_datetime_validator]
    update_dt: t.Annotated[datetime, before_datetime_validator]
    login_dt: t.Annotated[datetime, before_datetime_validator]
    is_superuser: bool


class CreateUserShema(UserShema):
    ident: UUID = Field(default_factory=uuid4)
    sign_dt: t.Annotated[datetime, before_datetime_validator] = Field(default_factory=datetime.now)
    update_dt: t.Annotated[datetime, before_datetime_validator] = Field(default_factory=datetime.now)
    login_dt: t.Annotated[datetime, before_datetime_validator] = Field(default_factory=datetime.now)
    is_superuser: bool = Field(default=False)


    @model_validator(mode="before")
    @classmethod
    def hash_input_password(cls, data: dict) -> dict:
        if "password" not in data:
            raise ValueError("password is required")
        
        data["hashed_password"] = AuthService().hash_password(data["password"])

        return data


class UpdateUserShema(BaseUserShema):
    password: str | None = Field(default=None)
    is_superuser: bool | None = Field(default=None)
    

    def model_dump(self, *, mode: EmailStr | EmailStr | EmailStr = 'python', include: t.Set[int] | t.Set[EmailStr] | t.Dict[int, t.Any] | t.Dict[EmailStr, t.Any] | None = None, exclude: t.Set[int] | t.Set[EmailStr] | t.Dict[int, t.Any] | t.Dict[EmailStr, t.Any] | None = None, context: dict[str, t.Any] | None = None, by_alias: bool = False, exclude_unset: bool = False, exclude_defaults: bool = False, exclude_none: bool = False, round_trip: bool = False, warnings: bool | EmailStr | EmailStr | EmailStr = True, serialize_as_any: bool = False) -> dict[str, t.Any]:
        data = super().model_dump(mode=mode, include=include, exclude=exclude, context=context, by_alias=by_alias, exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, exclude_none=exclude_none, round_trip=round_trip, warnings=warnings, serialize_as_any=serialize_as_any)

        data["hashed_password"] = AuthService().hash_password(data["password"])

        del data["password"]

        return data
