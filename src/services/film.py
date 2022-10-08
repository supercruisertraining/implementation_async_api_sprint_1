import json
from functools import lru_cache
from typing import Optional, List

from fastapi import Depends

from models.film import Film
from services.cache import AbstractCache, get_cache
from services.storage import AbstractStorage, get_storage
from core.config import config


class FilmService:

    name = config.es_movies_index

    def __init__(self, cache: AbstractCache, storage: AbstractStorage):
        self.cache = cache
        self.storage = storage

    async def get_by_id(self, film_uuid: str) -> Optional[Film]:
        film = await self.cache.get_from_cache(key=film_uuid)
        if not film:
            film = await self.storage.get_object_by_id(index=self.name, object_id=film_uuid)
            if not film:
                return None
            await self.cache.put_to_cache(key=film_uuid, value=json.dumps(film))
        return Film(**film)

    async def search_films(self, search_query, page_size: int, page_number: int) -> List[Film]:
        query_body = {"query": {
            "bool": {
                "should": [
                    {"match": {"title": {"query": search_query, "fuzziness": "auto"}}},
                    {"match": {"description": {"query": search_query, "fuzziness": "1"}}},
                    {"nested": {
                        "path": "actors",
                        "query": {
                            "match": {
                                "actors.full_name": {
                                    "query": search_query,
                                    "fuzziness": "2"}
                            }
                        }
                    }
                    }
                ]
            }
        }
        }
        query_body.update({"size": page_size, "from": (page_number - 1) * page_size})
        film_list = await self.storage.get_object_list(index=self.name, query=json.dumps(query_body))
        return list(map(lambda x: Film(**x), film_list))

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
            query_body.update({"sort": {f'{sort_rule["field"]}.raw'
                                        if sort_rule["field"] in ("title",)
                                        else sort_rule["field"]:
                                            {"order": "desc" if sort_rule["desc"] else "asc"}}})
        film_list = await self.cache.get_from_cache(self.cache.cook_cache_key(self.name, page_number, page_size,
                                                                        sort_rule, filters_should))
        if not film_list:
            film_list = await self.storage.get_object_list(index=self.name, query=json.dumps(query_body))
            if film_list:
                await self.cache.put_to_cache(self.cache.cook_cache_key(self.name, page_number, page_size,
                                                                        sort_rule, filters_should),
                                              value=json.dumps(film_list))
            else:
                return []
        return list(map(lambda x: Film(**x), film_list))


@lru_cache()
def get_film_service(
        cache: AbstractCache = Depends(get_cache),
        storage: AbstractStorage = Depends(get_storage),
) -> FilmService:
    return FilmService(cache=cache, storage=storage)
