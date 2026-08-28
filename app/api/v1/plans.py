from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.models.plan import SubscriptionPlan
from app.schemas import PlanRead

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[PlanRead])
async def list_plans(db: AsyncSession = Depends(get_db)) -> list[SubscriptionPlan]:
    result = await db.execute(select(SubscriptionPlan))
    return list(result.scalars().all())
