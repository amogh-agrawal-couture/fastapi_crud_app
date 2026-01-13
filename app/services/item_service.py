from typing import Any, Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.item_repository import ItemRepository
from app.schemas import ItemCreate
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
        item: ItemCreate,
    ) -> ItemDB:
        # Example business rule
        if item.text and len(item.text) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item text too long",
            )

        return await self.repository.create(db, item)

    async def list_items(
        self,
        db: AsyncSession,
        limit: int,
    ) -> Sequence[Any]:
        if limit > 100:
            limit = 100  # business constraint
        return await self.repository.list(db, limit)

    async def get_item(
        self,
        db: AsyncSession,
        item_id: int,
    ) -> ItemDB:
        item = await self.repository.get_by_id(db, item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )
        return item
