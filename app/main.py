from fastapi import FastAPI
from app.routers.items import router as items_router

app = FastAPI(title= "FastAPI APP")

app.include_router(items_router)
    

