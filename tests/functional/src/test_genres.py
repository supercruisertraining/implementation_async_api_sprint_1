from urllib.parse import urljoin

import pytest
import aiohttp

from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_genres_endpoint(push_genres_data):
    session = aiohttp.ClientSession()
    url = urljoin(test_settings.api_base_url, "/api/v1/genres/")
    async with session.get(url) as response:
        body = await response.json()

    await session.close()
    assert len(body) == 3


@pytest.mark.asyncio
async def test_genre_detail_endpoint(push_genres_data, get_test_data):
    genre_1 = get_test_data["genres"]["genre_1"].copy()
    session = aiohttp.ClientSession()
    url = urljoin(test_settings.api_base_url, f"/api/v1/genres/{genre_1['id']}")
    async with session.get(url) as response:
        body = await response.json()

    await session.close()
    assert body["name"] == genre_1["name"]
