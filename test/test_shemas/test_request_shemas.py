import pytest

from shemas.request_shemas import *


@pytest.mark.usefixtures("request_refresh_tokens")
def test_refresh_token_request_shema(request_refresh_tokens: list[dict]):
    for el in request_refresh_tokens:
        expression = el.pop("expression")

        request_shema = RefreshTokenRequestShema.model_validate(el)

        assert expression == request_shema.dump_expression().__str__()
