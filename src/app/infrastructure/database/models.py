from datetime import datetime
import uuid

from sqlalchemy.orm import Mapped, DeclarativeBase
from sqlalchemy.schema import Index
import sqlalchemy as sa


__all__ = [
    "Base",
    "UserModel",
    "RefreshTokenModel",
    "PermissionModel"
]


class Base(DeclarativeBase): ...


class UserModel(Base):
    __tablename__ = "user_table"

    ident: Mapped[uuid.UUID] = sa.Column(sa.UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = sa.Column(sa.String(), nullable=False)
    login: Mapped[str] = sa.Column(sa.String(), unique=True, nullable=False)
    hashed_password: Mapped[str] = sa.Column(sa.String(), nullable=False)
    email: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    project: Mapped[list[str] | None] = sa.Column(sa.ARRAY(sa.String), nullable=True)
    sign_dt: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)
    update_dt: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)
    login_dt: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)

    __table_args__ = (
        Index("user_ident_idx", ident),
        Index("user_login_idx", login),
        Index("user_project_idx", project)
    )


class RefreshTokenModel(Base):
    __tablename__ = "refresh_token_table"

    ident: Mapped[uuid.UUID] = sa.Column(sa.UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_ident: Mapped[uuid.UUID] = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey("user_table.ident", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    token: Mapped[str] = sa.Column(sa.String(), nullable=False, unique=True)
    revoked: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False)
    exp_dt: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)
    gen_dt: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)

    __table_args__ = (
        Index("refresh_token_ident_idx", ident),
        Index("refresh_token_user_ident_idx", user_ident),
        Index("token_idx", token),
        Index("revoked_idx", revoked)
    )


class PermissionModel(Base):
    __tablename__ = "permission_table"

    ident: Mapped[uuid.UUID] = sa.Column(sa.UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_ident: Mapped[uuid.UUID] = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey("user_table.ident", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    is_super_user: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False)

    personal_data_get: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    personal_data_create: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    personal_data_update: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    personal_data_delete: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)

    personal_naks_certification_data_get: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    personal_naks_certification_data_create: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    personal_naks_certification_data_update: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    personal_naks_certification_data_delete: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)

    ndt_data_get: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    ndt_data_create: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    ndt_data_update: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    ndt_data_delete: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)

    acst_data_get: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    acst_data_create: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    acst_data_update: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    acst_data_delete: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)

    acst_file_download: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    acst_file_upload: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)

    personal_naks_certification_file_download: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    personal_naks_certification_file_upload: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)

    personal_naks_protocol_file_download: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)
    personal_naks_protocol_file_upload: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False, default=False)


    __table_args__ = (
        Index("permission_ident_idx", ident),
        Index("permission_user_ident_idx", user_ident)
    )
