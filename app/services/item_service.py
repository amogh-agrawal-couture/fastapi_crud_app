from typing import Any, Sequence
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
import json

from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate, ItemOut
from app.models import ItemDB


class ItemService:
    """
    Contains business rules and validations.
    Talks to repository.
    """

    def __init__(self, repository: ItemRepository):
        self.repository = repository

    async def create_item(
            self,
            db: AsyncSession,
            redis: Redis,
            item: ItemCreate,
    ) -> ItemDB:
        # Example business rule
        if item.text and len(item.text) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item text too long",
            )

        # Create in database
        db_item = await self.repository.create(db, item)

        # Cache the new item
        cache_key = f"item:{db_item.id}"
        item_dict = ItemOut.model_validate(db_item).model_dump()
        await redis.setex(
            cache_key,
            3600,  # 1 hour TTL
            json.dumps(item_dict, default=str)
        )

        # Invalidate list cache
        await redis.delete("items:list:*")

        return db_item

    async def list_items(
            self,
            db: AsyncSession,
            redis: Redis,
            limit: int,
    ) -> Sequence[Any]:
        if limit > 100:
            limit = 100  # business constraint

        # Try cache first
        cache_key = f"items:list:{limit}"
        cached = await redis.get(cache_key)

        if cached:
            print(f"✓ Cache HIT for {cache_key}")
            cached_data = json.loads(cached)
            # Convert back to ItemDB objects
            return [ItemOut(**item) for item in cached_data]

        print(f"✗ Cache MISS for {cache_key}")

        # Get from database
        items = await self.repository.list(db, limit)

        # Cache the result
        items_dict = [ItemOut.model_validate(item).model_dump() for item in items]
        await redis.setex(
            cache_key,
            300,  # 5 minutes TTL
            json.dumps(items_dict, default=str)
        )

        return items

    async def get_item(
            self,
            db: AsyncSession,
            redis: Redis,
            item_id: int,
    ) -> ItemDB:
        # Try cache first
        cache_key = f"item:{item_id}"
        cached = await redis.get(cache_key)

        if cached:
            print(f"✓ Cache HIT for {cache_key}")
            return ItemDB(**json.loads(cached))

        print(f"✗ Cache MISS for {cache_key}")

        # Get from database
        item = await self.repository.get_by_id(db, item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )

        # Cache the result
        item_dict = ItemOut.model_validate(item).model_dump()
        await redis.setex(
            cache_key,
            3600,  # 1 hour TTL
            json.dumps(item_dict, default=str)
        )

        return item