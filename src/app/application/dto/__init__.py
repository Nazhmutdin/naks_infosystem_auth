from app.application.dto.data import UserDTO, CreateUserDTO, UpdateUserDTO, CurrentUser, RefreshTokenDTO, CreateRefreshTokenDTO, UpdateRefreshTokenDTO


def convert_create_refresh_token_dto_to_refresh_token_dto(dto: CreateRefreshTokenDTO) -> RefreshTokenDTO:
    return RefreshTokenDTO(
        ident=dto.ident,
        user_ident=dto.user_ident,
        token=dto.token,
        revoked=dto.revoked,
        gen_dt=dto.gen_dt,
        exp_dt=dto.exp_dt
    )


def convert_refresh_token_dto_to_create_refresh_token_dto(dto: RefreshTokenDTO) -> CreateRefreshTokenDTO:
    return RefreshTokenDTO(
        ident=dto.ident,
        user_ident=dto.user_ident,
        token=dto.token,
        revoked=dto.revoked,
        gen_dt=dto.gen_dt,
        exp_dt=dto.exp_dt
    )
