from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Response, Request, Query
from dishka import FromDishka
from dishka.integrations.fastapi import inject

from app.application.dto import UserDTO
from app.application.common.exc import UserNotFound
from app.application.interactors import (
    CreateUserInteractor, 
    UpdateUserInteractor, 
    GetUserInteractor, 
    DeleteUserInteractor,
    ValidateAccessInteractor
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
    validate_access: FromDishka[ValidateAccessInteractor],
    request: Request,
    data: CreateUserShema
) -> Response:
    
    await validate_access(access_token, request)

    await create_user(data.to_dto())

    return Response(
        "user successfully created"
    )


@user_router.get("/")
@inject
async def get_user(
    ident: Annotated[UUID, Query()],
    access_token: FromDishka[AccessTokenDTO],
    validate_access: FromDishka[ValidateAccessInteractor],
    request: Request,
    get_user: FromDishka[GetUserInteractor]
) -> UserDTO:
    
    await validate_access(access_token, request)

    res = await get_user(ident)

    if res:
        return res
    
    raise UserNotFound(ident)


@user_router.patch("/")
@inject
async def update_user(
    ident: Annotated[UUID, Query()],
    data: UpdateUserShema,
    access_token: FromDishka[AccessTokenDTO],
    validate_access: FromDishka[ValidateAccessInteractor],
    request: Request,
    update_user: FromDishka[UpdateUserInteractor]
) -> Response:
    
    await validate_access(access_token, request)
    
    await update_user(ident, data.to_dto())

    return Response(
        f"user {ident} successfully updated"
    )


@user_router.delete("/")
@inject
async def delete_user(
    ident: Annotated[UUID, Query()],
    access_token: FromDishka[AccessTokenDTO],
    validate_access: FromDishka[ValidateAccessInteractor],
    request: Request,
    delete_user: FromDishka[DeleteUserInteractor]
) -> Response:
    
    await validate_access(access_token, request)
    
    await delete_user(ident)

    return Response(
        f"user {ident} successfully deleted"
    )
