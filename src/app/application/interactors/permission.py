from app.application.dto import UserDTO
from app.application.common.exc import AccessForbidden


class CheckUserActionPermissionInteractor:
    async def __call__(self, user: UserDTO):
            if not user.is_superuser:
                raise AccessForbidden()
