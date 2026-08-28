from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.borrowing import Borrowing
from app.models.plan import SubscriptionPlan
from app.models.user import User
from app.schemas.user import UserCreate


async def create_user(db: AsyncSession, payload: UserCreate) -> User:
    plan = await db.get(SubscriptionPlan, payload.subscription_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Subscription plan not found")

    user = User(
        email=payload.email,
        name=payload.name,
        age=payload.age,
        subscription_id=payload.subscription_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user, attribute_names=["subscription_plan"])
    return user


async def get_user(db: AsyncSession, user_id: int) -> User:
    user = await db.get(User, user_id, options=[joinedload(User.subscription_plan)])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def list_user_borrowings(db: AsyncSession, user_id: int) -> list[Borrowing]:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(Borrowing)
        .options(joinedload(Borrowing.item))
        .where(Borrowing.user_id == user_id)
        .order_by(Borrowing.borrowed_at.desc())
    )
    return list(result.scalars().all())
