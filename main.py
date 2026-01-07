from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from schemas import ItemCreate, ItemOut
import crud

app = FastAPI()

@app.get("/")
def home():
    return "Hello User, Welcome to the Async FastAPI Application! \n FOR THE UI ADD /docs# TO THE URL"

@app.post("/items", response_model=ItemOut)
async def create_item(

    item: ItemCreate,
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_item(db, item)

@app.get("/items", response_model=list[ItemOut])
async def list_items(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    return await crud.list_items(db, limit)

@app.get("/items/{itemId}", response_model=ItemOut)
async def read_item(
    itemId: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        item = await crud.get_item(db, itemId)
        return item
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Item not found. Error:{e}")
    

