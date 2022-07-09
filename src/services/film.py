from functools import lru_cache
from typing import Optional, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_uuid: str) -> Optional[Film]:
        film = await self._film_from_cache(film_uuid)
        if not film:
            film = await self._get_film_from_elastic(film_uuid)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def get_film_list(self, page_size: int, page_number: int,
                            sort_rule: dict = None, filters_should: dict = None) -> List[Film]:
        query_body = {}
        query_body.update({"size": page_size, "from": (page_number - 1)*page_size})
        filter_fields = filters_should.keys() if filters_should else []
        nested_search_by_id_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "nested": {
                                "path": field,
                                "query": {
                                    "bool": {
                                        "should": [
                                            {
                                                "match": {f"{field}.id": field_value}
                                            } for field_value in filters_should[field]
                                        ]
                                    }
                                }
                            }
                        } for field in filter_fields
                    ]
                }
            }
        } if filters_should else dict()
        query_body.update(nested_search_by_id_query)
        if sort_rule:
            query_body.update({"sort": {sort_rule["field"]: {"order": "desc" if sort_rule["desc"] else "asc"}}})
        film_list = await self._get_film_list_by_strict_search(query_body=query_body)
        return film_list

    async def _get_film_list_by_strict_search(self, query_body) -> List[Film]:
        try:
            film_list = await self.elastic.search(index="movies", body=query_body)
        except NotFoundError:
            return []
        return list(map(lambda x: Film(**x["_source"]), film_list["hits"]["hits"]))

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get("movies", film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
