import asyncio
import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from shop.external_api import (
    fetch_product_with_retry,
    fetch_one_limited,
    fetch_multiple_products_async,
)


@pytest.mark.asyncio
async def test_fetch_product_with_retry_success():
    """Проверка успешного выполнения запроса с первого раза."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "name": "Laptop", "price": 25000.0}
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    result = await fetch_product_with_retry(mock_client, "http://test/products/1")

    assert result["name"] == "Laptop"
    mock_client.get.assert_called_once_with("http://test/products/1")


@pytest.mark.asyncio
async def test_fetch_product_with_retry_failure_then_success():
    """Проверка работы retry logic: ошибка на первой попытке и успех на второй."""
    mock_ok_response = MagicMock()
    mock_ok_response.status_code = 200
    mock_ok_response.json.return_value = {"id": 1, "name": "Mouse"}
    mock_ok_response.raise_for_status.return_value = None

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = [
        httpx.RequestError("Network error"),
        mock_ok_response,
    ]

    result = await fetch_product_with_retry(mock_client, "http://test/products/1", attempts=3)

    assert result["name"] == "Mouse"
    assert mock_client.get.call_count == 2