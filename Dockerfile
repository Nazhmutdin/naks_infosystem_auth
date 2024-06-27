FROM python:3.12.2-slim

WORKDIR /src

RUN apt-get update && apt-get install -y libpq-dev

COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache

COPY . .