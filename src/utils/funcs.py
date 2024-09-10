from datetime import datetime, timedelta, UTC

from src.services.auth_service import AuthService
from src.settings import Settings


def validate_refresh_token(v: str) -> bool:
    return AuthService().validate_refresh_token(v)


def current_utc_datetime() -> datetime:
    return datetime.now(UTC)


def current_utc_datetime_without_timezone() -> datetime:
    return current_utc_datetime().replace(tzinfo=None)


def refresh_token_expiration_dt() -> datetime:
    return current_utc_datetime() + timedelta(hours=Settings.REFRESH_TOKEN_LIFETIME_HOURS())


def access_token_expiration_dt() -> datetime:
    return current_utc_datetime() + timedelta(minutes=Settings.ACCESS_TOKEN_LIFETIME_MINUTES())


def refresh_token_expiration_dt_without_timezone() -> datetime:
    return current_utc_datetime_without_timezone() + timedelta(days=1)
