from pydantic import BaseModel

from app.models.enums import Genre, ItemType


class ItemCreate(BaseModel):
    title: str
    type: ItemType
    genre: Genre
    author: str
    description: str | None = None


class ItemRead(BaseModel):
    id: int
    title: str
    type: ItemType
    genre: Genre
    author: str
    description: str | None
    available: bool

    model_config = {"from_attributes": True}
