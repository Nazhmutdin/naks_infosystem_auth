from uuid import UUID, uuid4
from datetime import datetime

from pydantic import ValidationInfo, EmailStr, Field, field_validator, model_validator
from naks_library import BaseShema, to_datetime

from src.services.auth_service import AuthService


class BaseUserShema(BaseShema):
    __fields_ignore__ = ["ident"]
    
    name: str | None = Field(default=None) 
    login: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    sign_dt: datetime | None = Field(default=None)
    update_dt: datetime | None = Field(default=None)
    login_dt: datetime | None = Field(default=None)


class UserShema(BaseUserShema):
    ident: UUID
    login: str
    name: str
    hashed_password: str
    sign_dt: datetime
    update_dt: datetime
    login_dt: datetime
    is_superuser: bool


    @field_validator("sign_dt", "update_dt", "login_dt", mode="before")
    @classmethod
    def validate_datetimes(cls, v: str | datetime | None, info: ValidationInfo):
        
        try:
            return to_datetime(v)
        except:
            raise ValueError(f"{info.field_name} got invalid date data ({v})")


class CreateUserShema(UserShema):
    ident: UUID = Field(default_factory=uuid4)
    sign_dt: datetime = Field(default_factory=datetime.now)
    update_dt: datetime = Field(default_factory=datetime.now)
    login_dt: datetime = Field(default_factory=datetime.now)
    is_superuser: bool = Field(default=False)


    @model_validator(mode="before")
    @classmethod
    def hash_input_password(cls, data: dict) -> dict:
        if "password" not in data:
            raise ValueError("password is required")
        
        data["hashed_password"] = AuthService().hash_password(data["password"])

        return data


class UpdateUserShema(BaseUserShema):
    hashed_password: str | None = Field(default=None)
    is_superuser: bool | None = Field(default=None)
        

    @field_validator("sign_dt", "update_dt", "login_dt", mode="before")
    @classmethod
    def validate_datetimes(cls, v: str | datetime | None, info: ValidationInfo):
        if v == None:
            return None
        
        try:
            return to_datetime(v)
        except:
            raise ValueError(f"{info.field_name} got invalid date data ({v})")


    @model_validator(mode="before")
    @classmethod
    def hash_input_password(cls, data: dict) -> dict:
        if "password" in data:
        
            data["hashed_password"] = AuthService().hash_password(data["password"])

            return data
