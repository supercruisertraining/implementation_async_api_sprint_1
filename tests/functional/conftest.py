import os
import json

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


@pytest.fixture(scope='module')
def get_test_data():
    with open(os.path.join(os.path.dirname(__file__), "test_data.json"), "r") as r_f:
        return json.load(r_f)
