from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers.items import router as items_router
from app.cache import init_redis, close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_redis()
    yield
    # Shutdown
    await close_redis()

app = FastAPI(title="FastAPI APP", lifespan=lifespan)

app.include_router(items_router)
    

