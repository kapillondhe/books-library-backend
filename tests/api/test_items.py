from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import make_item


class TestListItemsRoute:
    async def test_returns_empty_list_when_no_items(self, client: AsyncClient):
        response = await client.get("/api/v1/items")
        assert response.status_code == 200
        assert response.json() == []

    async def test_returns_created_items(self, client: AsyncClient, db_session: AsyncSession):
        await make_item(db_session, title="Book One")
        await make_item(db_session, title="Book Two")

        response = await client.get("/api/v1/items")
        assert response.status_code == 200
        titles = {item["title"] for item in response.json()}
        assert titles == {"Book One", "Book Two"}


class TestCreateItemRoute:
    async def test_create_item_returns_201(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/items",
            json={"title": "New Book", "type": "BOOK", "genre": "FICTION", "author": "An Author"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["title"] == "New Book"
        assert body["available"] is True

    async def test_create_item_with_invalid_type_returns_422(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/items",
            json={"title": "New Book", "type": "DVD", "genre": "FICTION", "author": "An Author"},
        )
        assert response.status_code == 422
