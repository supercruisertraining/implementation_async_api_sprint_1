from urllib.parse import urljoin

import pytest
import aiohttp

from tests.functional.settings import test_settings


@pytest.mark.parametrize("query_data, expected_answer",
                         [
                             (
                                     {"query": "курцин"},
                                     {"length": 1, "title": "Меч"}
                             ),
                             (
                                     {"query": "мяч"},
                                     {"length": 1, "title": "Меч"}
                             ),
                             (
                                     {"query": "жексон", "page[size]": 100, "page[number]": 1},
                                     {"length": 60, "title": "Просто Джексон"}
                             )
                         ]
                         )
@pytest.mark.asyncio
async def test_search_endpoint(push_movies_data, query_data, expected_answer):
    session = aiohttp.ClientSession()
    url = urljoin(test_settings.api_base_url, "/api/v1/films/search/")
    async with session.get(url, params=query_data) as response:
        body = await response.json()

    await session.close()

    assert len(body) == expected_answer["length"]
    assert body[0]["title"] == expected_answer["title"]


@pytest.mark.asyncio
async def test_film_endpoint(push_movies_data):
    session = aiohttp.ClientSession()
    url = urljoin(test_settings.api_base_url, "/api/v1/films/47a18637-677d-4a0b-b0f8-051b11bb0adc/")
    async with session.get(url) as response:
        body = await response.json()

    await session.close()

    assert body["id"] == "47a18637-677d-4a0b-b0f8-051b11bb0adc"
    assert body["title"] == "Меч"


@pytest.mark.asyncio
async def test_films_endpoint(push_movies_data):
    session = aiohttp.ClientSession()
    url = urljoin(test_settings.api_base_url, "/api/v1/films/")
    async with session.get(url, params={"page[number]": 1, "page[size]": 100}) as response:
        body = await response.json()

    await session.close()

    assert len(body) == 61
