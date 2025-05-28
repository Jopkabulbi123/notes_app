import pytest
import httpx
import asyncio
import time


@pytest.mark.asyncio
async def test_views_performance():
    async with httpx.AsyncClient() as client:
        login_data = {"username": "testuser", "password": "testpass"}
        await client.post("http://localhost:8000/accounts/login/", data=login_data)

        endpoints = [
            ("/", "Note List"),
            ("/create/", "Note Create"),
        ]

        results = []
        for url, name in endpoints:
            start_time = time.time()
            response = await client.get(f"http://localhost:8000{url}")
            elapsed = time.time() - start_time
            print(f"{name} - Status: {response.status_code}, Time: {elapsed:.3f}s")
            results.append((name, elapsed))

        print("\nPerformance Results:")
        for name, elapsed in results:
            print(f"{name}: {elapsed:.3f}s")
        total_time = sum(t for _, t in results)
        print(f"Total time: {total_time:.3f}s")