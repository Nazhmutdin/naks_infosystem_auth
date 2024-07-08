from fastapi import APIRouter, Response, Request, Depends

from src.services.auth_service import AuthService
from src.api.v1.dependencies import authorize_dependency, authenticatе_dependency, update_tokens_dependency, AccessToken, RefreshToken
from src.utils.funcs import refresh_token_expiration_dt, access_token_expiration_dt
from src._types import AccessTokenShema


v1_router = APIRouter()


@v1_router.post("/authorizate")
async def authorizate(
    tokens: tuple[RefreshToken, AccessToken] = Depends(authorize_dependency)
    ) -> Response: 

    response = Response()

    response.set_cookie("refresh_token", tokens[0], httponly=True, path="/auth", expires=refresh_token_expiration_dt())
    response.set_cookie("access_token", tokens[1], httponly=True, path="/v1", expires=access_token_expiration_dt())

    return response


@v1_router.post("/authenticate")
async def authenticate(access_token: AccessToken = Depends(authenticatе_dependency)) -> Response:
    
    response = Response()

    response.set_cookie("access_token", access_token, httponly=True, path="/v1", expires=access_token_expiration_dt())

    return response


@v1_router.post("/update-tokens")
async def update_tokens(tokens: tuple[RefreshToken, AccessToken] = Depends(update_tokens_dependency)) -> Response:
    
    response = Response()

    response.set_cookie("refresh_token", tokens[0], httponly=True, path="/auth", expires=refresh_token_expiration_dt())
    response.set_cookie("access_token", tokens[1], httponly=True, path="/v1", expires=access_token_expiration_dt())

    return response


@v1_router.get("/validate-access")
async def validate_access(request: Request) -> Response:
    access_token = request.cookies.get("access_token")
    service = AuthService()
    
    if not access_token:
        return Response(
            status_code=401
        )
    elif not service.validate_access_token(access_token):
        return Response(
            "invalid token",
            403
        )
    else:
        access_token = AccessTokenShema.from_token(access_token)

        if access_token.is_expired:
            return Response(
                "token_expired",
                403
            )
        else:
            return Response(
                status_code=200
            )
