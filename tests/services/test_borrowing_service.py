from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.models.plan import SubscriptionPlan
from app.models.transaction import Transaction
from app.models.user import User
from app.services.borrowing_service import (
    MONTHLY_TRANSACTION_LIMIT,
    order_item,
    return_item,
)
from tests.factories import make_item


class TestSubscriptionQuota:
    async def test_order_succeeds_within_book_quota(self, db_session, adult_user):
        item = await make_item(db_session)
        borrowing = await order_item(db_session, adult_user.id, item.id)
        assert borrowing.item_id == item.id
        assert borrowing.returned_at is None

    async def test_order_fails_when_book_quota_exceeded(self, db_session, adult_user, silver_plan):
        for i in range(silver_plan.max_books):
            item = await make_item(db_session, title=f"Book {i}")
            await order_item(db_session, adult_user.id, item.id)

        overflow_item = await make_item(db_session, title="Overflow Book")
        with pytest.raises(HTTPException) as exc_info:
            await order_item(db_session, adult_user.id, overflow_item.id)
        assert exc_info.value.status_code == 400
        assert "quota" in exc_info.value.detail.lower()

    async def test_order_succeeds_up_to_higher_plan_quota(self, db_session, gold_plan):
        user = User(email="gold@example.com", name="Gold User", age=30, subscription_id=gold_plan.id)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        for i in range(gold_plan.max_books):
            item = await make_item(db_session, title=f"Book {i}")
            await order_item(db_session, user.id, item.id)

        overflow_item = await make_item(db_session, title="Overflow Book")
        with pytest.raises(HTTPException) as exc_info:
            await order_item(db_session, user.id, overflow_item.id)
        assert exc_info.value.status_code == 400

    async def test_magazine_quota_is_independent_of_book_quota(self, db_session, gold_plan):
        user = User(email="gold-magazine@example.com", name="Gold Magazine User", age=30, subscription_id=gold_plan.id)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        book = await make_item(db_session, type="BOOK")
        magazine = await make_item(db_session, type="MAGAZINE", title="A Magazine")

        await order_item(db_session, user.id, book.id)
        borrowing = await order_item(db_session, user.id, magazine.id)
        assert borrowing.item_id == magazine.id

    async def test_silver_plan_allows_no_magazines(self, db_session, adult_user):
        magazine = await make_item(db_session, type="MAGAZINE", title="A Magazine")
        with pytest.raises(HTTPException) as exc_info:
            await order_item(db_session, adult_user.id, magazine.id)
        assert exc_info.value.status_code == 400
        assert "quota" in exc_info.value.detail.lower()


class TestCrimeGenreAgeRestriction:
    async def test_minor_cannot_order_crime_item(self, db_session, minor_user):
        item = await make_item(db_session, genre="CRIME")
        with pytest.raises(HTTPException) as exc_info:
            await order_item(db_session, minor_user.id, item.id)
        assert exc_info.value.status_code == 400

    async def test_adult_can_order_crime_item(self, db_session, adult_user):
        item = await make_item(db_session, genre="CRIME")
        borrowing = await order_item(db_session, adult_user.id, item.id)
        assert borrowing.item_id == item.id

    async def test_minor_can_order_non_crime_item(self, db_session, minor_user):
        item = await make_item(db_session, genre="FANTASY")
        borrowing = await order_item(db_session, minor_user.id, item.id)
        assert borrowing.item_id == item.id


class TestMonthlyTransactionLimit:
    async def test_tenth_transaction_succeeds(self, db_session, adult_user):
        now = datetime.now(timezone.utc)
        for _ in range(MONTHLY_TRANSACTION_LIMIT - 1):
            db_session.add(Transaction(user_id=adult_user.id, type="ORDER", created_at=now))
        await db_session.commit()

        item = await make_item(db_session)
        borrowing = await order_item(db_session, adult_user.id, item.id)
        assert borrowing.item_id == item.id

    async def test_eleventh_transaction_fails(self, db_session, adult_user):
        now = datetime.now(timezone.utc)
        for _ in range(MONTHLY_TRANSACTION_LIMIT):
            db_session.add(Transaction(user_id=adult_user.id, type="ORDER", created_at=now))
        await db_session.commit()

        item = await make_item(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await order_item(db_session, adult_user.id, item.id)
        assert exc_info.value.status_code == 400
        assert "limit" in exc_info.value.detail.lower()

    async def test_transactions_from_previous_month_do_not_count(self, db_session, adult_user):
        last_month = datetime.now(timezone.utc).replace(day=1) - timedelta(days=1)
        for _ in range(MONTHLY_TRANSACTION_LIMIT):
            db_session.add(Transaction(user_id=adult_user.id, type="ORDER", created_at=last_month))
        await db_session.commit()

        item = await make_item(db_session)
        borrowing = await order_item(db_session, adult_user.id, item.id)
        assert borrowing.item_id == item.id


class TestDoubleBorrowAndReturn:
    async def test_cannot_order_unavailable_item(self, db_session, adult_user, gold_plan):
        other_user = User(email="other@example.com", name="Other User", age=30, subscription_id=gold_plan.id)
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        item = await make_item(db_session)
        await order_item(db_session, other_user.id, item.id)

        with pytest.raises(HTTPException) as exc_info:
            await order_item(db_session, adult_user.id, item.id)
        assert exc_info.value.status_code == 400
        assert "not available" in exc_info.value.detail.lower()

    async def test_item_available_again_after_return(self, db_session, adult_user):
        item = await make_item(db_session)
        await order_item(db_session, adult_user.id, item.id)

        borrowing = await return_item(db_session, adult_user.id, item.id)
        assert borrowing.returned_at is not None

        await db_session.refresh(item)
        assert item.available is True

    async def test_returning_unborrowed_item_fails(self, db_session, adult_user):
        item = await make_item(db_session, available=True)
        with pytest.raises(HTTPException) as exc_info:
            await return_item(db_session, adult_user.id, item.id)
        assert exc_info.value.status_code == 404

    async def test_can_reorder_item_after_return(self, db_session, adult_user):
        item = await make_item(db_session)
        await order_item(db_session, adult_user.id, item.id)
        await return_item(db_session, adult_user.id, item.id)

        borrowing = await order_item(db_session, adult_user.id, item.id)
        assert borrowing.returned_at is None
