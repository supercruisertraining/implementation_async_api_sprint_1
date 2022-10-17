from urllib.parse import urljoin

import pytest
import aiohttp

from tests.functional.settings import test_settings


@pytest.mark.parametrize("query_data, expected_answer",
                         [
                             (
                                     {"query": "курцин"},
                                     {"length": 1, "movie_key": "movie_1"}
                             ),
                             (
                                     {"query": "мяч"},
                                     {"length": 1, "movie_key": "movie_1"}
                             ),
                             (
                                     {"query": "жексон", "page[size]": 100, "page[number]": 1},
                                     {"length": 60, "movie_key": "movie_2"}
                             )
                         ]
                         )
@pytest.mark.asyncio
async def test_search_endpoint(push_movies_data, get_test_data, query_data, expected_answer):
    movies = get_test_data["movies"].copy()
    session = aiohttp.ClientSession()
    url = urljoin(test_settings.api_base_url, "/api/v1/films/search/")
    async with session.get(url, params=query_data) as response:
        body = await response.json()

    await session.close()

    assert len(body) == expected_answer["length"]
    assert body[0]["title"] == movies[expected_answer["movie_key"]]["title"]


@pytest.mark.asyncio
async def test_film_endpoint(push_movies_data, get_test_data):
    movie_1 = get_test_data["movies"]["movie_1"].copy()
    session = aiohttp.ClientSession()
    url = urljoin(test_settings.api_base_url, f"/api/v1/films/{movie_1['id']}/")
    async with session.get(url) as response:
        body = await response.json()

    await session.close()

    assert body["id"] == movie_1["id"]
    assert body["title"] == movie_1["title"]


@pytest.mark.asyncio
async def test_films_endpoint(push_movies_data):
    session = aiohttp.ClientSession()
    url = urljoin(test_settings.api_base_url, "/api/v1/films/")
    async with session.get(url, params={"page[number]": 1, "page[size]": 100}) as response:
        body = await response.json()

    await session.close()

    assert len(body) == 61
