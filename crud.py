from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import ItemDB
from schemas import ItemCreate

async def create_item(db: AsyncSession, item: ItemCreate):
    db_item = ItemDB(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def list_items(db: AsyncSession, limit: int):
    result = await db.execute(
        select(ItemDB).limit(limit)
    )
    return result.scalars().all()

async def get_item(db: AsyncSession, item_id: int):
    result = await db.execute(
        select(ItemDB).where(ItemDB.id == item_id)
    )
    return result.scalar_one_or_none()
