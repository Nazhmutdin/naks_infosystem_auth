from fastapi import APIRouter, Response, Depends

from main.dependencies import (
    CreateUserInteractorDep,
    GetUserInteractorDep,
    UpdateUserInteractorDep,
    DeleteUserInteractorDep,
    check_user_crud_action_access
)
from src.presentation.shemas import CreateUserShema, UpdateUserShema
from src.application.dto import UserDTO
from src.application.common.exc import UserNotFound
 

user_router = APIRouter(
    prefix="/v1"
)


@user_router.post("/user", dependencies=[Depends(check_user_crud_action_access)])
async def create_user(
    create: CreateUserInteractorDep,
    user_data: CreateUserShema
) -> Response:
    await create(user_data.to_dto())

    return Response(
        "user successfully created"
    )


@user_router.get("/user/{ident}", dependencies=[Depends(check_user_crud_action_access)])
async def get_user(
    ident: str,
    get: GetUserInteractorDep
) -> UserDTO:

    res = await get(ident)

    if res:
        return res
    
    raise UserNotFound(ident)


@user_router.patch("/user/{ident}", dependencies=[Depends(check_user_crud_action_access)])
async def update_user(
    ident: str,
    user_data: UpdateUserShema,
    update: UpdateUserInteractorDep
) -> Response:
    
    await update(ident, user_data.to_dto())

    return Response(
        f"user {ident} successfully updated"
    )


@user_router.delete("/user/{ident}", dependencies=[Depends(check_user_crud_action_access)])
async def delete_user(
    ident: str,
    delete: DeleteUserInteractorDep
) -> Response:
    
    await delete(ident)

    return Response(
        f"user {ident} successfully deleted"
    )
