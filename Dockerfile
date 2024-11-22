FROM python:3.12.2-slim as build

ENV POETRY_HOME=/opt/poetry \
    POETRY_VENV=/opt/poetry-venv \
    POETRY_CACHE_DIR=/opt/.cache \
    SECRET_KEY=$SECRET_KEY 

RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry


#==================================================================================
FROM build as base
#==================================================================================


COPY --from=build ${POETRY_VENV} ${POETRY_VENV}

ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /auth_service

COPY poetry.lock pyproject.toml ./

RUN poetry install --without dev

COPY . .
