from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.factories import make_item


class TestOrderRoute:
    async def test_order_returns_success_result(self, client: AsyncClient, db_session: AsyncSession, adult_user):
        item = await make_item(db_session)
        response = await client.post("/api/v1/borrowings/order", json={"user_id": adult_user.id, "item_id": item.id})
        assert response.status_code == 200
        body = response.json()
        assert body["item_id"] == item.id
        assert body["success"] is True
        assert body["borrowed_at"] is not None

    async def test_order_unavailable_item_returns_400(self, client: AsyncClient, db_session: AsyncSession, adult_user):
        item = await make_item(db_session, available=False)
        response = await client.post("/api/v1/borrowings/order", json={"user_id": adult_user.id, "item_id": item.id})
        assert response.status_code == 400

    async def test_order_with_unknown_user_returns_404(self, client: AsyncClient, db_session: AsyncSession):
        item = await make_item(db_session)
        response = await client.post("/api/v1/borrowings/order", json={"user_id": 999, "item_id": item.id})
        assert response.status_code == 404


class TestReturnRoute:
    async def test_return_returns_borrowing_with_returned_at_set(
        self, client: AsyncClient, db_session: AsyncSession, adult_user
    ):
        item = await make_item(db_session)
        await client.post("/api/v1/borrowings/order", json={"user_id": adult_user.id, "item_id": item.id})

        response = await client.post(
            "/api/v1/borrowings/return", json={"user_id": adult_user.id, "item_ids": [item.id]}
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["success"] is True
        assert body[0]["item_id"] == item.id

    async def test_return_unborrowed_item_reports_failure(
        self, client: AsyncClient, db_session: AsyncSession, adult_user
    ):
        item = await make_item(db_session)
        response = await client.post(
            "/api/v1/borrowings/return", json={"user_id": adult_user.id, "item_ids": [item.id]}
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["success"] is False
        assert body[0]["item_id"] == item.id

    async def test_return_multiple_items_in_one_request(
        self, client: AsyncClient, db_session: AsyncSession, gold_plan
    ):
        user = User(email="multi@example.com", name="Multi User", age=30, subscription_id=gold_plan.id)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        item_a = await make_item(db_session, title="Item A")
        item_b = await make_item(db_session, title="Item B")
        await client.post("/api/v1/borrowings/order", json={"user_id": user.id, "item_id": item_a.id})
        await client.post("/api/v1/borrowings/order", json={"user_id": user.id, "item_id": item_b.id})

        response = await client.post(
            "/api/v1/borrowings/return", json={"user_id": user.id, "item_ids": [item_a.id, item_b.id]}
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 2
        assert all(result["success"] for result in body)
        assert {result["item_id"] for result in body} == {item_a.id, item_b.id}

    async def test_return_mixed_success_and_failure(
        self, client: AsyncClient, db_session: AsyncSession, adult_user
    ):
        borrowed_item = await make_item(db_session, title="Borrowed Item")
        unborrowed_item = await make_item(db_session, title="Unborrowed Item")
        await client.post("/api/v1/borrowings/order", json={"user_id": adult_user.id, "item_id": borrowed_item.id})

        response = await client.post(
            "/api/v1/borrowings/return",
            json={"user_id": adult_user.id, "item_ids": [borrowed_item.id, unborrowed_item.id]},
        )
        assert response.status_code == 200
        body = response.json()
        results_by_id = {result["item_id"]: result for result in body}
        assert results_by_id[borrowed_item.id]["success"] is True
        assert results_by_id[unborrowed_item.id]["success"] is False
