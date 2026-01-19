from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import ItemDB
from app.schemas.item import ItemCreate

class ItemRepository:
    """
    Handles all database operations for Item.
    No business logic here.
    """

    async def create(
        self,
        db: AsyncSession,
        item: ItemCreate,
    ) -> ItemDB:
        db_item = ItemDB(**item.model_dump())
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    async def list(
        self,
        db: AsyncSession,
        limit: int,
    ) -> Sequence[Any]:
        result = await db.execute(
            select(ItemDB).limit(limit)
        )
        return result.scalars().all()

    async def get_by_id(
        self,
        db: AsyncSession,
        item_id: int,
    ) -> ItemDB | None:
        result = await db.execute(
            select(ItemDB).where(ItemDB.id == item_id)
        )
        return result.scalar_one_or_none()
