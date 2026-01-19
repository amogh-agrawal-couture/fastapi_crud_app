# app/models/item.py
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class ItemDB(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
