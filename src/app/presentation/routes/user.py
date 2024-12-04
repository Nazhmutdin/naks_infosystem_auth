from fastapi import APIRouter, Response
from dishka import FromDishka
from dishka.integrations.fastapi import inject

from app.application.dto import UserDTO
from app.application.common.exc import UserNotFound
from app.application.interactors import (
    CreateUserInteractor, 
    UpdateUserInteractor, 
    GetUserInteractor, 
    DeleteUserInteractor,
    ValidateSuperUserAccessInteractor
)
from app.presentation.shemas import CreateUserShema, UpdateUserShema
from app.infrastructure.dto import AccessTokenDTO
 

user_router = APIRouter(
    prefix="/v1/user"
)

@user_router.post("/")
@inject
async def create_user(
    create_user: FromDishka[CreateUserInteractor],
    access_token: FromDishka[AccessTokenDTO],
    validate_access: FromDishka[ValidateSuperUserAccessInteractor],
    data: CreateUserShema
) -> Response:
    
    await validate_access(access_token)

    await create_user(data.to_dto())

    return Response(
        "user successfully created"
    )


@user_router.get("/{ident}")
@inject
async def get_user(
    ident: str,
    access_token: FromDishka[AccessTokenDTO],
    validate_access: FromDishka[ValidateSuperUserAccessInteractor],
    get_user: FromDishka[GetUserInteractor]
) -> UserDTO:
    
    await validate_access(access_token)

    res = await get_user(ident)

    if res:
        return res
    
    raise UserNotFound(ident)


@user_router.patch("/{ident}")
@inject
async def update_user(
    ident: str,
    data: UpdateUserShema,
    access_token: FromDishka[AccessTokenDTO],
    validate_access: FromDishka[ValidateSuperUserAccessInteractor],
    update_user: FromDishka[UpdateUserInteractor]
) -> Response:
    
    await validate_access(access_token)
    
    await update_user(ident, data.to_dto())

    return Response(
        f"user {ident} successfully updated"
    )


@user_router.delete("/{ident}")
@inject
async def delete_user(
    ident: str,
    access_token: FromDishka[AccessTokenDTO],
    validate_access: FromDishka[ValidateSuperUserAccessInteractor],
    delete_user: FromDishka[DeleteUserInteractor]
) -> Response:
    
    await validate_access(access_token)
    
    await delete_user(ident)

    return Response(
        f"user {ident} successfully deleted"
    )
