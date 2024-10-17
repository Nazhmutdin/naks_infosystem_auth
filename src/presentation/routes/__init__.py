# from src.presentation.routes.auth import auth_router
from src.presentation.routes.user import user_router
from src.presentation.routes.exc_handler import (
    current_user_not_found_handler,
    user_not_found_handler,
    access_forbidden_handler,
    refresh_token_cookie_not_found_handler,
    access_token_cookie_not_found_handler,
    refresh_token_not_found_handler
)
from src.presentation.routes.root import register_routes
