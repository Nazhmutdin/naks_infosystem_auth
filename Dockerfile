FROM python:3.12.2-slim as build

WORKDIR /src

COPY requirements.txt .
RUN pip3 wheel --no-cache-dir --wheel-dir /src/wheels -r requirements.txt

FROM python:3.12.2-slim

WORKDIR /src

COPY --from=build /src/wheels /wheels
COPY --from=build /src/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY . .