from sqlalchemy.exc import IntegrityError


__all__ = [
    "CreateDBException",
    "GetDBException",
    "GetManyDBException",
    "UpdateDBException",
    "DeleteDBException",
    "DBServiceException",
    "FieldValidationException"
]


class CreateDBException(Exception):
    def __init__(self, exc: IntegrityError) -> None:
        super().__init__(exc.detail)


class GetDBException(Exception):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)


class GetManyDBException(Exception):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)


class UpdateDBException(Exception):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)


class DeleteDBException(Exception):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)


class DBServiceException(Exception):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)


class FieldValidationException(ValueError):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)
