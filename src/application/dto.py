from typing import Annotated
from datetime import datetime
from uuid import UUID

from pydantic.dataclasses import dataclass
from pydantic import EmailStr
from naks_library.utils.validators import plain_datetime_serializer


@dataclass
class UserDTO:
    ident: UUID
    login: str
    name: str
    email: EmailStr | None
    hashed_password: str
    sign_dt: Annotated[datetime, plain_datetime_serializer] 
    update_dt: Annotated[datetime, plain_datetime_serializer] 
    login_dt: Annotated[datetime, plain_datetime_serializer] 
    is_superuser: bool


@dataclass
class CreateUserDTO(UserDTO): ...


@dataclass
class UpdateUserDTO:
    name: str | None
    login: str | None
    email: EmailStr | None
    sign_dt: datetime | None
    update_dt: datetime | None
    login_dt: datetime | None
    is_superuser: bool | None