from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.presentation.routes import register_routes
from src.main.dependencies import container


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    yield

    await container.engine.dispose()


app = FastAPI(lifespan=lifespan)


register_routes(app)
