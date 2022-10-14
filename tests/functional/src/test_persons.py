from urllib.parse import urljoin

import pytest
import aiohttp

from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_persons_endpoint(push_persons_data):
    session = aiohttp.ClientSession()
    url = urljoin(test_settings.api_base_url, "/api/v1/persons/")
    async with session.get(url, params={"sort": "-full_name"}) as response:
        body = await response.json()

    await session.close()
    assert len(body) == 3


@pytest.mark.asyncio
async def test_person_detail_endpoint(push_persons_data):
    session = aiohttp.ClientSession()
    url = urljoin(test_settings.api_base_url, "/api/v1/persons/15a35990-2d50-4147-9d2f-420214138700")
    async with session.get(url) as response:
        body = await response.json()

    await session.close()
    assert body["full_name"] == "Роман Курцын"