import json
from typing import Optional, List
from functools import lru_cache

from fastapi import Depends
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from db.elastic import get_elastic
from db.redis import get_redis

from models.genre import GenreDetail, Genre


GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService:
    name = "genres"

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis):
        self.elastic = elastic
        self.redis = redis

    async def get_genre_by_id(self, genre_id: str) -> Optional[GenreDetail]:
        genre_data = await self._get_genre_by_id_from_cache(genre_id)
        if not genre_data:
            genre_data = await self._get_genre_from_elastic_by_id(genre_id=genre_id)
            if genre_data:
                await self._put_data_to_cache(field=genre_id, value=genre_data.json())
        return genre_data

    async def _get_genre_from_elastic_by_id(self, genre_id: str) -> Optional[GenreDetail]:
        try:
            doc = await self.elastic.get("genres", genre_id)
        except NotFoundError:
            return None
        return GenreDetail(**doc["_source"])

    async def _get_genre_list_from_elastic(self):
        try:
            doc = await self.elastic.search(index=self.name)
        except NotFoundError:
            return None
        return list(map(lambda x: Genre(**x["_source"]), doc["hits"]["hits"]))

    async def get_genre_list(self) -> List[Genre]:
        genres_list = await self._get_genre_list_from_cache(self.name)
        if not genres_list:
            genres_list = await self._get_genre_list_from_elastic()
            if genres_list:
                await self._put_data_to_cache(field=self._cook_cache_key(),
                                              value=json.dumps([x.json() for x in genres_list]))
        return genres_list

    async def _get_genre_by_id_from_cache(self, genre_id: str) -> Optional[GenreDetail]:
        genre_raw = await self.redis.get(genre_id)
        if not genre_raw:
            return None
        return GenreDetail.parse_raw(genre_raw)

    async def _get_genre_list_from_cache(self, key: str) -> List[Genre]:
        person_list_raw = await self.redis.get(key)
        if not person_list_raw:
            return []
        return list(map(lambda x: Genre.parse_raw(x), json.loads(person_list_raw)))

    async def _put_data_to_cache(self, field: str, value: str):
        await self.redis.set(key=field, value=value, expire=GENRE_CACHE_EXPIRE_IN_SECONDS)

    def _cook_cache_key(self) -> str:
        return self.name


@lru_cache
def get_genre_service(elastic: AsyncElasticsearch = Depends(get_elastic),
                      redis: Redis = Depends(get_redis)) -> GenreService:
    return GenreService(elastic=elastic, redis=redis)
