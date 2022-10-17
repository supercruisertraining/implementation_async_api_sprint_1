import uuid
import json

import pytest
from elasticsearch import AsyncElasticsearch, RequestError

from tests.functional.settings import test_settings
from tests.functional.utils.helpers import create_es_index


@pytest.fixture(scope="module")
async def create_movies_index(es_client):
    elastic = es_client
    # Test Index Created
    try:
        await create_es_index(elastic=elastic, index_name=test_settings.es_movies_index,
                              mapping_file=test_settings.es_movies_index_mapping_file)
    except RequestError as e:
        pass

    yield elastic
    # Удаляем созданный тестовый индекс
    elastic = AsyncElasticsearch(hosts=test_settings.es_host_url, validate_cert=False, use_ssl=False)
    await elastic.indices.delete(index=test_settings.es_movies_index)
    await elastic.close()


@pytest.fixture(scope="module")
async def push_movies_data(create_movies_index, get_test_data):
    elastic = create_movies_index
    test_data = get_test_data["movies"].copy()
    es_data = []
    for _ in range(60):
        cur_film = test_data["movie_2"].copy()
        cur_film["id"] = str(uuid.uuid4())
        es_data.append(cur_film)
    es_data.append(test_data["movie_1"])
    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': test_settings.es_movies_index, '_id': row["id"]}}),
            json.dumps(row)
        ])

    str_query = '\n'.join(bulk_query) + '\n'
    response = await elastic.bulk(str_query.encode("utf-8"), refresh=True)
    if response['errors']:
        raise Exception('Ошибка записи данных в Elasticsearch')
