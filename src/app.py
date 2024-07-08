from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.routes import v1_router


app = FastAPI()


origins = [
    "http://localhost:8000",
    "https://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app = FastAPI()

app.include_router(v1_router, prefix="/auth/v1")
