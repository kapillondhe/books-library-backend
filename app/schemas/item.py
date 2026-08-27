from pydantic import BaseModel


class ItemCreate(BaseModel):
    title: str
    type: str        # BOOK / MAGAZINE
    genre: str       # e.g. CRIME, FANTASY, FICTION
    author: str
    description: str | None = None
    image_path: str | None = None


class ItemRead(BaseModel):
    id: int
    title: str
    type: str
    genre: str
    author: str
    description: str | None
    image_path: str | None
    available: bool

    model_config = {"from_attributes": True}
