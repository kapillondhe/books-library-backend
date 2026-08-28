from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.borrowing import Borrowing
from app.models.item import Item
from app.models.plan import SubscriptionPlan
from app.schemas.user import UserCreate
from app.services.user_service import create_user, get_user, list_user_borrowings


class TestCreateUser:
    async def test_creates_user_with_valid_plan(self, db_session: AsyncSession, silver_plan: SubscriptionPlan):
        payload = UserCreate(email="new@example.com", name="New User", age=22, subscription_id=silver_plan.id)
        user = await create_user(db_session, payload)
        assert user.id is not None
        assert user.email == "new@example.com"
        assert user.subscription_plan.id == silver_plan.id

    async def test_fails_when_plan_does_not_exist(self, db_session: AsyncSession):
        payload = UserCreate(email="new@example.com", name="New User", age=22, subscription_id=999)
        with pytest.raises(HTTPException) as exc_info:
            await create_user(db_session, payload)
        assert exc_info.value.status_code == 404


class TestGetUser:
    async def test_returns_existing_user(self, db_session: AsyncSession, adult_user):
        user = await get_user(db_session, adult_user.id)
        assert user.id == adult_user.id
        assert user.subscription_plan is not None

    async def test_fails_when_user_does_not_exist(self, db_session: AsyncSession):
        with pytest.raises(HTTPException) as exc_info:
            await get_user(db_session, 999)
        assert exc_info.value.status_code == 404


class TestListUserBorrowings:
    async def test_fails_when_user_does_not_exist(self, db_session: AsyncSession):
        with pytest.raises(HTTPException) as exc_info:
            await list_user_borrowings(db_session, 999)
        assert exc_info.value.status_code == 404

    async def test_returns_empty_list_when_no_borrowings(self, db_session: AsyncSession, adult_user):
        borrowings = await list_user_borrowings(db_session, adult_user.id)
        assert borrowings == []

    async def test_returns_borrowings_ordered_most_recent_first(self, db_session: AsyncSession, adult_user):
        item_a = Item(title="Book A", type="BOOK", genre="FICTION", author="Author", available=False)
        item_b = Item(title="Book B", type="BOOK", genre="FICTION", author="Author", available=False)
        db_session.add_all([item_a, item_b])
        await db_session.commit()
        await db_session.refresh(item_a)
        await db_session.refresh(item_b)

        now = datetime.now(timezone.utc)
        older = Borrowing(user_id=adult_user.id, item_id=item_a.id, borrowed_at=now - timedelta(days=1))
        newer = Borrowing(user_id=adult_user.id, item_id=item_b.id, borrowed_at=now)
        db_session.add_all([older, newer])
        await db_session.commit()

        borrowings = await list_user_borrowings(db_session, adult_user.id)
        assert [b.item_id for b in borrowings] == [item_b.id, item_a.id]
