from naks_library.interactors import BaseGetInteractor, BaseCreateInteractor, BaseUpdateInteractor, BaseDeleteInteractor

from src.application.dto import UserDTO, CreateUserDTO, UpdateUserDTO


class CreateUserInteractor(BaseCreateInteractor[CreateUserDTO]): ...


class GetUserInteractor(BaseGetInteractor[UserDTO]): ...


class UpdateUserInteractor(BaseUpdateInteractor[UpdateUserDTO]): ...


class DeleteUserInteractor(BaseDeleteInteractor): ...
