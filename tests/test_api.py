import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from shop.api import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "E-Commerce REST API is running"}


def test_create_and_get_product(sample_category):
    # 1. Створюємо продукт, використовуючи id категорії з фікстури
    prod_resp = client.post(
        "/products",
        json={"name": "Laptop", "price": 25000.0, "quantity": 10, "category_id": sample_category.id},
    )
    assert prod_resp.status_code == 201
    data = prod_resp.json()
    assert data["name"] == "Laptop"
    prod_id = data["id"]

    # 2. Отримуємо продукт за id
    get_resp = client.get(f"/products/{prod_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["price"] == 25000.0


def test_validation_error():
    resp = client.post(
        "/products",
        json={"name": "X", "price": -10, "quantity": 5, "category_id": 1},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_async_api_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200