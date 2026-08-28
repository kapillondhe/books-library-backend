from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core import get_db
from app.models.borrowing import Borrowing
from app.schemas import BorrowingRead, OrderRequest, ReturnRequest
from app.services import order_item, return_item

router = APIRouter(prefix="/borrowings", tags=["borrowings"])


async def _with_item(db: AsyncSession, borrowing: Borrowing) -> Borrowing:
    result = await db.execute(
        select(Borrowing)
        .options(joinedload(Borrowing.item))
        .where(Borrowing.id == borrowing.id)
    )
    return result.scalar_one()


@router.post("/order", response_model=BorrowingRead)
async def order(payload: OrderRequest, db: AsyncSession = Depends(get_db)):
    borrowing = await order_item(db, payload.user_id, payload.item_id)
    return await _with_item(db, borrowing)


@router.post("/return", response_model=BorrowingRead)
async def return_(payload: ReturnRequest, db: AsyncSession = Depends(get_db)):
    borrowing = await return_item(db, payload.user_id, payload.item_id)
    return await _with_item(db, borrowing)
