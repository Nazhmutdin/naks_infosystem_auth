from uuid import UUID

from naks_library.interfaces import ICrudGateway

from app.application.dto import (
    UserDTO,
    CreateUserDTO,
    UpdateUserDTO,
    RefreshTokenDTO,
    CreateRefreshTokenDTO, 
    UpdateRefreshTokenDTO
)


class UserGateway(ICrudGateway[UserDTO, CreateUserDTO, UpdateUserDTO]):
    async def get_by_login(self, login: str) -> UserDTO | None: ...
    

class RefreshTokenGateway(ICrudGateway[RefreshTokenDTO, CreateRefreshTokenDTO, UpdateRefreshTokenDTO]): 
    async def revoke_all_user_tokens(self, ident: UUID): ...
