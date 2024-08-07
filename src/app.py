from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.routes import v1_router


app = FastAPI()


origins = [
    "http://localhost:5173",
    "https://localhost:5173",
    "http://rhi-qa-infosystem.ru",
    "https://rhi-qa-infosystem.ru",
    "http://api.rhi-qa-infosystem.ru",
    "https://api.rhi-qa-infosystem.ru"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(v1_router, prefix="/auth/v1")
