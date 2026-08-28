from httpx import AsyncClient
from app.models.plan import SubscriptionPlan


class TestListPlansRoute:
    async def test_returns_empty_list_when_no_plans(self, client: AsyncClient):
        response = await client.get("/api/v1/plans")
        assert response.status_code == 200
        assert response.json() == []

    async def test_returns_created_plans(self, client: AsyncClient, silver_plan: SubscriptionPlan, gold_plan: SubscriptionPlan):
        response = await client.get("/api/v1/plans")
        assert response.status_code == 200
        names = {plan["name"] for plan in response.json()}
        assert names == {"Silver", "Gold"}
