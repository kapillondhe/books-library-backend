from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import SubscriptionPlan
from tests.factories import make_item


class TestCreateUserRoute:
    async def test_create_user_returns_201(self, client: AsyncClient, silver_plan: SubscriptionPlan):
        response = await client.post(
            "/api/v1/users",
            json={
                "email": "route@example.com",
                "name": "Route User",
                "age": 30,
                "subscription_id": silver_plan.id,
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["email"] == "route@example.com"
        assert body["subscription_plan"]["id"] == silver_plan.id

    async def test_create_user_with_unknown_plan_returns_404(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/users",
            json={"email": "route@example.com", "name": "Route User", "age": 30, "subscription_id": 999},
        )
        assert response.status_code == 404

    async def test_create_user_with_invalid_payload_returns_422(self, client: AsyncClient, silver_plan: SubscriptionPlan):
        response = await client.post(
            "/api/v1/users",
            json={"email": "not-an-email", "name": "Route User", "age": 30, "subscription_id": silver_plan.id},
        )
        assert response.status_code == 422


class TestGetUserRoute:
    async def test_returns_existing_user(self, client: AsyncClient, adult_user):
        response = await client.get(f"/api/v1/users/{adult_user.id}")
        assert response.status_code == 200
        assert response.json()["id"] == adult_user.id

    async def test_returns_404_for_unknown_user(self, client: AsyncClient):
        response = await client.get("/api/v1/users/999")
        assert response.status_code == 404


class TestListUserBorrowingsRoute:
    async def test_returns_empty_list_when_no_borrowings(self, client: AsyncClient, adult_user):
        response = await client.get(f"/api/v1/users/{adult_user.id}/borrowings")
        assert response.status_code == 200
        assert response.json() == []

    async def test_returns_404_for_unknown_user(self, client: AsyncClient):
        response = await client.get("/api/v1/users/999/borrowings")
        assert response.status_code == 404

    async def test_returns_borrowed_item_details(self, client: AsyncClient, db_session: AsyncSession, adult_user):
        item = await make_item(db_session)

        order_response = await client.post(
            "/api/v1/borrowings/order", json={"user_id": adult_user.id, "item_id": item.id}
        )
        assert order_response.status_code == 200

        response = await client.get(f"/api/v1/users/{adult_user.id}/borrowings")
        assert response.status_code == 200
        borrowings = response.json()
        assert len(borrowings) == 1
        assert borrowings[0]["item"]["id"] == item.id
