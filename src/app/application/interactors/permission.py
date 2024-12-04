from app.application.interfaces.gateways import PermissionGateway
from app.application.dto import UserDTO, PermissionDTO


class GetUserPermissionsInteractor:
    def __init__(
        self,
        permission_gateway: PermissionGateway
    ) -> None:
        self.permission_gateway = permission_gateway


    async def __call__(
        self,
        user: UserDTO
    ) -> PermissionDTO | None:
        return await self.permission_gateway.get_by_user_ident(user.ident)
