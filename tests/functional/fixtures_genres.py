import json

import pytest
from elasticsearch import AsyncElasticsearch, RequestError

from tests.functional.settings import test_settings
from tests.functional.utils.helpers import create_es_index


@pytest.fixture(scope="module")
async def create_genres_index(es_client):
    elastic = es_client
    # Test Index Created
    try:
        await create_es_index(elastic=elastic, index_name=test_settings.es_genres_index,
                              mapping_file=test_settings.es_genres_index_mapping_file)
    except RequestError as e:
        pass

    yield elastic
    # Удаляем созданный тестовый индекс
    elastic = AsyncElasticsearch(hosts=test_settings.es_host_url, validate_cert=False, use_ssl=False)
    await elastic.indices.delete(index=test_settings.es_genres_index)
    await elastic.close()


@pytest.fixture(scope="module")
async def push_genres_data(create_genres_index, get_test_data):
    elastic = create_genres_index
    test_data = get_test_data["genres"].copy()
    es_data = [test_data["genre_1"], test_data["genre_2"], test_data["genre_3"]]
    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': test_settings.es_genres_index, '_id': row["id"]}}),
            json.dumps(row)
        ])
    str_query = '\n'.join(bulk_query) + '\n'
    response = await elastic.bulk(str_query.encode("utf-8"), refresh=True)
    if response['errors']:
        raise Exception('Ошибка записи данных в Elasticsearch')
