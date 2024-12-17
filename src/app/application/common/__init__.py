from enum import StrEnum


class ExceptionCodes(StrEnum):
    USER_NOT_FOUND = "user_not_found"
    INVALID_PASSWORD = "invalid_password"
    INVALID_REFRESH_TOKEN = "invalid_refresh_token"
    INVALID_ACCESS_TOKEN = "invalid_access_token"
    ACCESS_FORBIDDEN = "access_forbidden"
    REFRESH_TOKEN_COOKIE_NOT_FOUND = "refresh_token_cookie_not_found"
    ACCESS_TOKEN_COOKIE_NOT_FOUND = "access_token_cookie_not_found"
    REFRESH_TOKEN_NOT_FOUND = "refresh_token_not_found"
    REFRESH_TOKEN_REVOKED = "refresh_token_revoked"
    REFRESH_TOKEN_EXPIRED = "refresh_token_expired"
    ACCESS_TOKEN_EXPIRED = "access_token_expired"
    PERMISSION_DATA_NOT_FOUND = "permission_data_not_found"
    ORIGINAL_METHOD_NOT_FOUND = "original_method_not_found"
    ORIGINAL_URI_NOT_FOUND = "original_uri_not_found"
