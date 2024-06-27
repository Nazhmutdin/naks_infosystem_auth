from fastapi import FastAPI

from src.api.v1.routes import v1_router


app = FastAPI()

app.include_router(v1_router, prefix="/api/auth/v1")
