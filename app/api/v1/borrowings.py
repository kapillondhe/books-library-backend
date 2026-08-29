from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.schemas import OrderRequest, OrderResult, ReturnItemResult, ReturnRequest
from app.services import order_item, return_items

router = APIRouter(prefix="/borrowings", tags=["borrowings"])


@router.post("/order", response_model=OrderResult)
async def order(payload: OrderRequest, db: AsyncSession = Depends(get_db)):
    borrowing = await order_item(db, payload.user_id, payload.item_id)
    return OrderResult(
        item_id=payload.item_id,
        success=True,
        message="Item ordered successfully",
        borrowed_at=borrowing.borrowed_at,
    )


@router.post("/return", response_model=list[ReturnItemResult])
async def return_(payload: ReturnRequest, db: AsyncSession = Depends(get_db)):
    return await return_items(db, payload.user_id, payload.item_ids)
