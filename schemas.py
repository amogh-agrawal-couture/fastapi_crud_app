from pydantic import BaseModel

class ItemCreate(BaseModel):
    text: str | None = None
    is_active: bool = True

class ItemOut(ItemCreate):
    id: int

    class Config:
        from_attributes = True
