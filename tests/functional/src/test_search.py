import uuid
import json
from urllib.parse import urljoin

import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import RequestError
import aiohttp

from tests.functional.settings import test_settings
from tests.functional.utils.helpers import create_es_index


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
async def test_search(query_data, expected_answer):
    elastic = AsyncElasticsearch(hosts=test_settings.es_host_url, validate_cert=False, use_ssl=False)

    # Test Index Created
    try:
        await create_es_index(elastic=elastic, index_name=test_settings.es_movies_index,
                              mapping_file=test_settings.es_movies_index_mapping_file)
    except RequestError as e:
        pass


    # Add test Data
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
        'id': str(uuid.uuid4()),
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
    await elastic.close()
    if response['errors']:
        raise Exception('Ошибка записи данных в Elasticsearch')

    # Тестирование
    session = aiohttp.ClientSession()
    url = urljoin(test_settings.api_base_url, "/api/v1/films/search/")
    async with session.get(url, params=query_data) as response:
        body = await response.json()
        headers = response.headers
        status = response.status

    await session.close()
    # Удаляем созданный тестовый индекс
    elastic = AsyncElasticsearch(hosts=test_settings.es_host_url, validate_cert=False, use_ssl=False)
    await elastic.indices.delete(index=test_settings.es_movies_index)
    await elastic.close()

    assert len(body) == expected_answer["length"]
    assert body[0]["title"] == expected_answer["title"]

