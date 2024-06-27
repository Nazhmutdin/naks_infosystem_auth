from fastapi import APIRouter, Response, Depends

from src.api.v1.dependencies import authorize_dependency, authenticatе_dependency, update_tokens_dependency, AccessToken, RefreshToken
from src.utils.funcs import refresh_token_expiration_dt, access_token_expiration_dt


v1_router = APIRouter()


@v1_router.post("/authorizate")
async def authorizate(
    tokens: tuple[RefreshToken, AccessToken] = Depends(authorize_dependency)
    ) -> Response: 

    response = Response()

    response.set_cookie("refresh_token", tokens[0], httponly=True, secure=True, path="/auth", expires=refresh_token_expiration_dt())
    response.set_cookie("access_token", tokens[1], httponly=True, secure=True, path="/api/v1", expires=access_token_expiration_dt())

    return response


@v1_router.post("/authenticate")
async def authenticate(access_token: AccessToken = Depends(authenticatе_dependency)) -> Response:
    
    response = Response()

    response.set_cookie("access_token", access_token, secure=True, httponly=True, path="/api/v1", expires=access_token_expiration_dt())

    return response


@v1_router.post("/update-tokens")
async def update_tokens(tokens: tuple[RefreshToken, AccessToken] = Depends(update_tokens_dependency)) -> Response:
    
    response = Response()

    response.set_cookie("refresh_token", tokens[0], secure=True, httponly=True, path="/auth", expires=refresh_token_expiration_dt())
    response.set_cookie("access_token", tokens[1], secure=True, httponly=True, path="/api/v1", expires=access_token_expiration_dt())

    return response
