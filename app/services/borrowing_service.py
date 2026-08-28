from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.borrowing import Borrowing
from app.models.enums import ItemType, TransactionType
from app.models.item import Item
from app.models.transaction import Transaction
from app.models.user import User

MONTHLY_TRANSACTION_LIMIT = 10
CRIME_GENRE_MIN_AGE = 18
CRIME_GENRE = "CRIME"


async def count_monthly_transactions(db: AsyncSession, user_id: int) -> int:
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    result = await db.execute(
        select(func.count())
        .select_from(Transaction)
        .where(
            Transaction.user_id == user_id,
            Transaction.created_at >= month_start,
        )
    )
    return result.scalar_one()


async def count_active_borrowings(db: AsyncSession, user_id: int, item_type: ItemType) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(Borrowing)
        .join(Item, Item.id == Borrowing.item_id)
        .where(
            Borrowing.user_id == user_id,
            Borrowing.returned_at.is_(None),
            Item.type == item_type,
        )
    )
    return result.scalar_one()


async def order_item(db: AsyncSession, user_id: int, item_id: int) -> Borrowing:
    user = await db.get(User, user_id, options=[joinedload(User.subscription_plan)])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    item = await db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if not item.available:
        raise HTTPException(status_code=400, detail="Item is not available")

    if await count_monthly_transactions(db, user_id) >= MONTHLY_TRANSACTION_LIMIT:
        raise HTTPException(status_code=400, detail="Monthly transaction limit reached")

    if item.genre.upper() == CRIME_GENRE and user.age < CRIME_GENRE_MIN_AGE:
        raise HTTPException(status_code=400, detail="User does not meet the minimum age for this genre")

    plan = user.subscription_plan
    active_count = await count_active_borrowings(db, user_id, item.type)
    if item.type == ItemType.BOOK and active_count >= plan.max_books:
        raise HTTPException(status_code=400, detail="Book borrowing quota exceeded")
    if item.type == ItemType.MAGAZINE and active_count >= plan.max_magazines:
        raise HTTPException(status_code=400, detail="Magazine borrowing quota exceeded")

    borrowing = Borrowing(user_id=user_id, item_id=item_id)
    item.available = False
    db.add(borrowing)
    db.add(Transaction(user_id=user_id, type=TransactionType.ORDER))

    await db.commit()
    await db.refresh(borrowing)
    return borrowing


async def return_item(db: AsyncSession, user_id: int, item_id: int) -> Borrowing:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if await count_monthly_transactions(db, user_id) >= MONTHLY_TRANSACTION_LIMIT:
        raise HTTPException(status_code=400, detail="Monthly transaction limit reached")

    result = await db.execute(
        select(Borrowing).where(
            Borrowing.user_id == user_id,
            Borrowing.item_id == item_id,
            Borrowing.returned_at.is_(None),
        )
    )
    borrowing = result.scalar_one_or_none()
    if borrowing is None:
        raise HTTPException(status_code=404, detail="Active borrowing not found")

    item = await db.get(Item, item_id)

    borrowing.returned_at = datetime.now(timezone.utc)
    item.available = True
    db.add(Transaction(user_id=user_id, type=TransactionType.RETURN))

    await db.commit()
    await db.refresh(borrowing)
    return borrowing
