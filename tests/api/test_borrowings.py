from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import make_item


class TestOrderRoute:
    async def test_order_returns_borrowing_with_item(self, client: AsyncClient, db_session: AsyncSession, adult_user):
        item = await make_item(db_session)
        response = await client.post("/api/v1/borrowings/order", json={"user_id": adult_user.id, "item_id": item.id})
        assert response.status_code == 200
        body = response.json()
        assert body["item"]["id"] == item.id
        assert body["returned_at"] is None

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

        response = await client.post("/api/v1/borrowings/return", json={"user_id": adult_user.id, "item_id": item.id})
        assert response.status_code == 200
        assert response.json()["returned_at"] is not None

    async def test_return_unborrowed_item_returns_404(self, client: AsyncClient, db_session: AsyncSession, adult_user):
        item = await make_item(db_session)
        response = await client.post("/api/v1/borrowings/return", json={"user_id": adult_user.id, "item_id": item.id})
        assert response.status_code == 404
