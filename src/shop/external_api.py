import asyncio
import httpx

semaphore = asyncio.Semaphore(3)


async def fetch_product_with_retry(client: httpx.AsyncClient, url: str, attempts: int = 3) -> dict:
    for attempt in range(1, attempts + 1):
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except (httpx.RequestError, httpx.HTTPStatusError):
            if attempt == attempts:
                raise
            await asyncio.sleep(0.1 * attempt)
    raise RuntimeError("Unexpected retry state")


async def fetch_one_limited(client: httpx.AsyncClient, url: str) -> dict:
    async with semaphore:
        return await fetch_product_with_retry(client, url)


async def fetch_multiple_products_async(base_url: str, product_ids: list[int]) -> list[dict]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        tasks = [
            asyncio.create_task(
                fetch_one_limited(client, f"{base_url}/products/{pid}")
            )
            for pid in product_ids
        ]
        results = await asyncio.gather(*tasks)
        return list(results)