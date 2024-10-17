from dishka import Provider, Scope, provide, from_context
from naks_library.commiter import SqlAlchemyCommitter
from jose.exceptions import JWTError, JWTClaimsError
from fastapi import Request

from app.application.interfaces.gateways import UserGateway, RefreshTokenGateway
from app.application.dto import RefreshTokenDTO, CurrentUser
from app.application.interactors import (
    CreateUserInteractor, 
    GetUserInteractor, 
    UpdateUserInteractor, 
    DeleteUserInteractor,
    CreateRefreshTokenInteractor, 
    GetRefreshTokenInteractor, 
    UpdateRefreshTokenInteractor, 
    DeleteRefreshTokenInteractor,
    LoginUserInteractor, 
    AuthenticateUserInteractor, 
    UpdateUserTokensInteractor,
    LogoutUserInteractor,
    ValidateAccessInteractor,
    CheckUserActionPermissionInteractor
)
from app.application.common.exc import (
    CurrentUserNotFound,
    RefreshTokenCookieNotFound,
    AccessTokenCookieNotFound,
    RefreshTokenNotFound,
    InvalidRefreshToken,
    InvalidAccessToken
)
from app.infrastructure.services import PasswordHasher, JwtService
from app.infrastructure.database.mappers import UserMapper, RefreshTokenMapper
from app.infrastructure.dto import AccessTokenDTO


class ApplicationProvider(Provider):
    request = from_context(provides=Request, scope=Scope.REQUEST)

    @provide(scope=Scope.APP)
    def get_hasher(self) -> PasswordHasher:
        return PasswordHasher()


    @provide(scope=Scope.APP)
    def get_jwt_service(self) -> JwtService:
        return JwtService()


    @provide(scope=Scope.REQUEST)
    async def get_refresh_token(
        self,
        request: Request,
        jwt_service: JwtService,
        get_refresh_token: GetRefreshTokenInteractor
    ) -> RefreshTokenDTO:
        refresh_token_cookie = request.cookies.get("refresh_token")

        if refresh_token_cookie:
            try:
                refresh_token_payload = jwt_service.read_refresh_token(refresh_token_cookie)
            except (JWTError, JWTClaimsError):
                raise InvalidRefreshToken
            
            token_ident = refresh_token_payload["ident"]

            res = await get_refresh_token(token_ident)

            if res:
                return res
            
            raise RefreshTokenNotFound(token_ident)
        
        raise RefreshTokenCookieNotFound


    @provide(scope=Scope.REQUEST)
    async def get_access_token(
        self,
        request: Request,
        jwt_service: JwtService
    ) -> AccessTokenDTO:
        access_token_cookie = request.cookies.get("access_token")

        if access_token_cookie:
            try:
                access_token_payload = jwt_service.read_access_token(access_token_cookie)
            except (JWTError, JWTClaimsError):
                raise InvalidAccessToken

            return AccessTokenDTO(
                token=access_token_cookie,
                user_ident=access_token_payload["user_ident"],
                gen_dt=access_token_payload["gen_dt"],
                exp_dt=access_token_payload["exp_dt"]
            )
        
        raise AccessTokenCookieNotFound
    

    @provide(scope=Scope.REQUEST)
    async def get_current_user(
        self,
        access_token: AccessTokenDTO,
        get_user: GetUserInteractor
    ) -> CurrentUser:
        user = await get_user(access_token.user_ident)

        if user:
            return user
        
        raise CurrentUserNotFound(
            user_ident=access_token.user_ident,
            access_token=access_token.token
        )
    
    
    @provide(scope=Scope.REQUEST)
    async def get_user_gateway(
        self,
        committer: SqlAlchemyCommitter,
    ) -> UserGateway:
        return UserMapper(committer.session)
    
    
    @provide(scope=Scope.REQUEST)
    async def get_refresh_token_gateway(
        self,
        committer: SqlAlchemyCommitter,
    ) -> RefreshTokenGateway:
        return RefreshTokenMapper(committer.session)


    @provide(scope=Scope.REQUEST)
    async def get_create_user_interactor(
        self, 
        committer: SqlAlchemyCommitter,
        user_gateway: UserGateway
    ) -> CreateUserInteractor:

        return CreateUserInteractor(
            gateway=user_gateway,
            commiter=committer
        )


    @provide(scope=Scope.REQUEST)
    async def get_user_data_interactor(
        self, 
        user_gateway: UserGateway
    ) -> GetUserInteractor:

        return GetUserInteractor(
            gateway=user_gateway
        )


    @provide(scope=Scope.REQUEST)
    async def get_update_user_interactor(
        self, 
        committer: SqlAlchemyCommitter,
        user_gateway: UserGateway
    ) -> UpdateUserInteractor:

        return UpdateUserInteractor(
            gateway=user_gateway,
            commiter=committer
        )


    @provide(scope=Scope.REQUEST)
    async def get_delete_user_interactor(
        self, 
        committer: SqlAlchemyCommitter,
        user_gateway: UserGateway
    ) -> DeleteUserInteractor:

        return DeleteUserInteractor(
            gateway=user_gateway,
            commiter=committer
        )


    @provide(scope=Scope.REQUEST)
    async def get_create_refresh_token_interactor(
        self, 
        committer: SqlAlchemyCommitter,
        refresh_token_gateway: RefreshTokenGateway
    ) -> CreateRefreshTokenInteractor:

        return CreateRefreshTokenInteractor(
            gateway=refresh_token_gateway,
            commiter=committer
        )


    @provide(scope=Scope.REQUEST)
    async def get_refresh_token_data_interactor(
        self, 
        refresh_token_gateway: RefreshTokenGateway
    ) -> GetRefreshTokenInteractor:

        return GetRefreshTokenInteractor(
            gateway=refresh_token_gateway
        )


    @provide(scope=Scope.REQUEST)
    async def get_update_refresh_token_interactor(
        self, 
        committer: SqlAlchemyCommitter,
        refresh_token_gateway: RefreshTokenGateway
    ) -> UpdateRefreshTokenInteractor:

        return UpdateRefreshTokenInteractor(
            gateway=refresh_token_gateway,
            commiter=committer
        )


    @provide(scope=Scope.REQUEST)
    async def get_delete_refresh_token_interactor(
        self, 
        committer: SqlAlchemyCommitter,
        refresh_token_gateway: RefreshTokenGateway
    ) -> DeleteRefreshTokenInteractor:

        return DeleteRefreshTokenInteractor(
            gateway=refresh_token_gateway,
            commiter=committer
        )
    
    
    @provide(scope=Scope.REQUEST)
    async def get_login_user_interactor(
        self,
        user_gateway: UserGateway,
        refresh_token_gateway: RefreshTokenGateway,
        committer: SqlAlchemyCommitter,
        jwt_service: JwtService
    ) -> LoginUserInteractor:
        return LoginUserInteractor(
            user_gateway=user_gateway,
            refresh_token_gateway=refresh_token_gateway,
            commiter=committer,
            jwt_service=jwt_service
        )
    
    
    @provide(scope=Scope.REQUEST)
    async def get_authenticate_user_interactor(
        self,
        user_gateway: UserGateway,
        refresh_token_gateway: RefreshTokenGateway,
        committer: SqlAlchemyCommitter,
        jwt_service: JwtService
    ) -> AuthenticateUserInteractor:
        return AuthenticateUserInteractor(
            user_gateway=user_gateway,
            refresh_token_gateway=refresh_token_gateway,
            commiter=committer,
            jwt_service=jwt_service
        )
    
    
    @provide(scope=Scope.REQUEST)
    async def get_update_user_tokens_interactor(
        self,
        user_gateway: UserGateway,
        refresh_token_gateway: RefreshTokenGateway,
        committer: SqlAlchemyCommitter,
        jwt_service: JwtService
    ) -> UpdateUserTokensInteractor:
        return UpdateUserTokensInteractor(
            user_gateway=user_gateway,
            refresh_token_gateway=refresh_token_gateway,
            commiter=committer,
            jwt_service=jwt_service
        )
    
    
    @provide(scope=Scope.REQUEST)
    async def get_logout_user_interactor(
        self,
        refresh_token_gateway: RefreshTokenGateway,
        committer: SqlAlchemyCommitter
    ) -> LogoutUserInteractor:
        return LogoutUserInteractor(
            refresh_token_gateway=refresh_token_gateway,
            commiter=committer
        )
    
    
    @provide(scope=Scope.REQUEST)
    async def get_validate_access_interactor(self) -> ValidateAccessInteractor:
        return ValidateAccessInteractor()
    
    
    @provide(scope=Scope.REQUEST)
    async def get_check_user_action_permission_interactor(self) -> CheckUserActionPermissionInteractor:
        return CheckUserActionPermissionInteractor()
