import pytest
from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings


@pytest.fixture(scope='module')
async def es_client():
    elastic = AsyncElasticsearch(hosts=test_settings.es_host_url, validate_cert=False, use_ssl=False)
    yield elastic
    await elastic.close()

pytest_plugins = [
    "tests.functional.fixtures_films",
    "tests.functional.fixtures_genres",
    "tests.functional.fixtures_persons",
]
