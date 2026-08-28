from pydantic import BaseModel

from app.models.enums import ItemType


class ItemCreate(BaseModel):
    title: str
    type: ItemType
    genre: str       # free text, e.g. CRIME, FANTASY, FICTION
    author: str
    description: str | None = None


class ItemRead(BaseModel):
    id: int
    title: str
    type: ItemType
    genre: str
    author: str
    description: str | None
    available: bool

    model_config = {"from_attributes": True}
