# how to use routers and implement them and register them with app
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas import ItemCreate, ItemOut
from app import query

router = APIRouter(prefix="/items", tags=["Items"])

@router.post("/", response_model=ItemOut)
async def create_item(

    item: ItemCreate,
    db: AsyncSession = Depends(get_db)
):
    return await query.create_item(db, item)

@router.get("/list", response_model=list[ItemOut])
async def list_items(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    return await query.list_items(db, limit)

@router.get("/{itemId}", response_model=ItemOut)
async def read_item(
    itemId: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        item = await query.get_item(db, itemId)
        return item
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Item not found. Error:{e}")
