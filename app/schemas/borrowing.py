from datetime import datetime

from pydantic import BaseModel

from app.schemas.item import ItemRead


class OrderRequest(BaseModel):
    user_id: int
    item_id: int


class ReturnRequest(BaseModel):
    user_id: int
    item_ids: list[int]


class BorrowingRead(BaseModel):
    id: int
    user_id: int
    item_id: int
    borrowed_at: datetime
    returned_at: datetime | None
    item: ItemRead

    model_config = {"from_attributes": True}


class ReturnItemResult(BaseModel):
    item_id: int
    success: bool
    message: str


class OrderResult(BaseModel):
    item_id: int
    success: bool
    message: str
    borrowed_at: datetime
