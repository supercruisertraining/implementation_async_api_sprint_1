import uuid
import json

import pytest
from elasticsearch import AsyncElasticsearch, RequestError

from tests.functional.settings import test_settings
from tests.functional.utils.helpers import create_es_index


@pytest.fixture(scope='session')
async def es_client():
    elastic = AsyncElasticsearch(hosts=test_settings.es_host_url, validate_cert=False, use_ssl=False)
    yield elastic
    await elastic.close()


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
async def push_movies_data(create_movies_index):
    elastic = create_movies_index
    es_data = [{
        'id': str(uuid.uuid4()),
        'rating': 6,
        'genres': [{'id': '999', 'name': 'Боевик'}, {'id': '777', 'name': 'Детектив'}],
        'title': 'Просто Джексон',
        'description': 'Продолжение сериала "Улицы разбитых фонарей". Главный герой - Джексон',
        'creation_date': "2019-02-25",
        'directors': [{'id': '333', 'full_name': 'Леонид Пляскин'}],
        'actors': [
            {'id': '111', 'full_name': 'Дмитрий Быковский'},
            {'id': '222', 'full_name': 'Андрей Горбачев'}
        ],
        'writers': [
            {'id': '333', 'full_name': 'Леонид Пляскин'},
        ],
    } for _ in range(60)]
    es_data.append({
        'id': '47a18637-677d-4a0b-b0f8-051b11bb0adc',
        'rating': 10,
        'genres': [{'id': '999', 'name': 'Боевик'}, {'id': '777', 'name': 'Детектив'}],
        'title': 'Меч',
        'description': 'Эдуард Флёров и Роман Курцын в главной роли',
        'creation_date': "2022-02-25",
        'directors': [{'id': '121', 'full_name': 'Илья Куликов'}],
        'actors': [
            {'id': '131', 'full_name': 'Роман Курцын'},
            {'id': '141', 'full_name': 'Эдуард Флёров'},
        ],
        'writers': [
            {'id': '121', 'full_name': 'Илья Куликов'},
        ]
    })
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
