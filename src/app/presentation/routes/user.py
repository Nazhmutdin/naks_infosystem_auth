from fastapi import APIRouter, Response
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute

from app.presentation.shemas import CreateUserShema, UpdateUserShema
from app.application.dto import UserDTO, CurrentUser
from app.application.common.exc import UserNotFound
from app.application.interactors import (
    CreateUserInteractor, 
    UpdateUserInteractor, 
    GetUserInteractor, 
    DeleteUserInteractor, 
    CheckUserActionPermissionInteractor
)
 

user_router = APIRouter(
    prefix="/v1",
    route_class=DishkaRoute
)

@user_router.post("/user")
async def create_user(
    create_user: FromDishka[CreateUserInteractor],
    check_access: FromDishka[CheckUserActionPermissionInteractor],
    user: FromDishka[CurrentUser],
    data: CreateUserShema
) -> Response:

    # await check_access(user)

    await create_user(data.to_dto())

    return Response(
        "user successfully created"
    )


@user_router.get("/user/{ident}")
async def get_user(
    ident: str,
    check_access: FromDishka[CheckUserActionPermissionInteractor],
    user: FromDishka[CurrentUser],
    get_user: FromDishka[GetUserInteractor]
) -> UserDTO:

    await check_access(user)

    res = await get_user(ident)

    if res:
        return res
    
    raise UserNotFound(ident)


@user_router.patch("/user/{ident}")
async def update_user(
    check_access: FromDishka[CheckUserActionPermissionInteractor],
    user: FromDishka[CurrentUser],
    ident: str,
    data: UpdateUserShema,
    update_user: FromDishka[UpdateUserInteractor]
) -> Response:

    await check_access(user)
    
    await update_user(ident, data.to_dto())

    return Response(
        f"user {ident} successfully updated"
    )


@user_router.delete("/user/{ident}")
async def delete_user(
    check_access: FromDishka[CheckUserActionPermissionInteractor],
    user: FromDishka[CurrentUser],
    ident: str,
    delete_user: FromDishka[DeleteUserInteractor]
) -> Response:

    await check_access(user)
    
    await delete_user(ident)

    return Response(
        f"user {ident} successfully deleted"
    )
