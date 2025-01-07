from uuid import UUID, uuid4
from datetime import datetime
import typing as t

from pydantic import EmailStr, Field
from naks_library import BaseShema
from naks_library.utils.validators import before_optional_datetime_validator, before_datetime_validator, plain_datetime_serializer

from app.infrastructure.services.hasher import PasswordHasher
from app.application.dto import CreateUserDTO, UpdateUserDTO


class CreateUserShema(BaseShema):
    ident: UUID = Field(default_factory=uuid4)
    name: str
    login: str
    email: EmailStr | None = Field(default=None)
    projects: list[str] | None
    password: str
    sign_dt: t.Annotated[datetime, before_datetime_validator] = Field(default_factory=datetime.now)
    update_dt: t.Annotated[datetime, before_datetime_validator] = Field(default_factory=datetime.now)
    login_dt: t.Annotated[datetime, before_datetime_validator] = Field(default_factory=datetime.now)
    is_superuser: bool = Field(default=False)


    def to_dto(self) -> CreateUserDTO:
        return CreateUserDTO(
            ident=self.ident,
            login=self.login,
            name=self.name,
            email=self.email,
            projects=self.projects,
            hashed_password=PasswordHasher().hash(self.password),
            sign_dt=self.sign_dt,
            update_dt=self.update_dt,
            login_dt=self.login_dt,
            is_superuser=self.is_superuser
        )
    

class UserWithouPasswordShema(BaseShema):
    ident: UUID = Field(default_factory=uuid4)
    name: str
    email: EmailStr | None = Field(default=None)
    projects: list[str] | None
    sign_dt: t.Annotated[datetime, before_datetime_validator, plain_datetime_serializer] = Field(default_factory=datetime.now)
    update_dt: t.Annotated[datetime, before_datetime_validator, plain_datetime_serializer] = Field(default_factory=datetime.now)
    login_dt: t.Annotated[datetime, before_datetime_validator, plain_datetime_serializer] = Field(default_factory=datetime.now)
    is_superuser: bool = Field(default=False)


class UpdateUserShema(BaseShema):
    name: str | None = Field(default=None) 
    login: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    projects: list[str] | None
    password: str | None = Field(default=None)
    sign_dt: t.Annotated[datetime | None, before_optional_datetime_validator] = Field(default=None)
    update_dt: t.Annotated[datetime | None, before_optional_datetime_validator] = Field(default=None)
    login_dt: t.Annotated[datetime | None, before_optional_datetime_validator] = Field(default=None)
    is_superuser: bool | None = Field(default=None)


    def to_dto(self) -> UpdateUserDTO:
        return UpdateUserDTO(
            login=self.login,
            name=self.name,
            email=self.email,
            projects=self.projects,
            hashed_password=PasswordHasher().hash(self.password),
            sign_dt=self.sign_dt,
            update_dt=self.update_dt,
            login_dt=self.login_dt,
            is_superuser=self.is_superuser
        )
