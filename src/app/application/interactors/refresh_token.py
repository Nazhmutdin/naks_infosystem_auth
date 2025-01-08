from naks_library.interactors import BaseGetInteractor, BaseCreateInteractor, BaseUpdateInteractor, BaseDeleteInteractor

from app.application.dto import RefreshTokenDTO, CreateRefreshTokenDTO


class CreateRefreshTokenInteractor(BaseCreateInteractor[CreateRefreshTokenDTO]): ...


class GetRefreshTokenInteractor(BaseGetInteractor[RefreshTokenDTO]): ...


class UpdateRefreshTokenInteractor(BaseUpdateInteractor): ...


class DeleteRefreshTokenInteractor(BaseDeleteInteractor): ...
