from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.db import get_db
from app.cache import get_redis
from app.schemas.item import ItemCreate, ItemOut
from app.services.item_service import ItemService
from app.repositories.item_repository import ItemRepository

router = APIRouter(prefix="/items", tags=["Items"])

item_service = ItemService(ItemRepository())
@router.post("/", response_model=ItemOut)
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    return await item_service.create_item(db, redis, item)


@router.get("/list", response_model=list[ItemOut])
async def list_items(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    return await item_service.list_items(db, redis, limit)


@router.get("/{item_id}", response_model=ItemOut)
async def read_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    return await item_service.get_item(db, redis, item_id)