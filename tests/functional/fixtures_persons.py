import json

import pytest
from elasticsearch import AsyncElasticsearch, RequestError

from tests.functional.settings import test_settings
from tests.functional.utils.helpers import create_es_index


@pytest.fixture(scope="module")
async def create_persons_index(es_client):
    elastic = es_client
    # Test Index Created
    try:
        await create_es_index(elastic=elastic, index_name=test_settings.es_persons_index,
                              mapping_file=test_settings.es_persons_index_mapping_file)
    except RequestError as e:
        pass

    yield elastic
    # Удаляем созданный тестовый индекс
    elastic = AsyncElasticsearch(hosts=test_settings.es_host_url, validate_cert=False, use_ssl=False)
    await elastic.indices.delete(index=test_settings.es_persons_index)
    await elastic.close()


@pytest.fixture(scope="module")
async def push_persons_data(create_persons_index):
    elastic = create_persons_index
    es_data = [{'id': '15a35990-2d50-4147-9d2f-420214138700', 'full_name': 'Роман Курцын'},
               {'id': '20096d83-26c0-450d-be7a-f745bd23a44f', 'full_name': 'Эдуард Флёров'},
               {'id': '972e565f-0126-4f24-961e-2572e4ebf006', 'full_name': 'Дмитрий Быковский'}]
    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': test_settings.es_persons_index, '_id': row["id"]}}),
            json.dumps(row)
        ])
    str_query = '\n'.join(bulk_query) + '\n'
    response = await elastic.bulk(str_query.encode("utf-8"), refresh=True)
    if response['errors']:
        raise Exception('Ошибка записи данных в Elasticsearch')
