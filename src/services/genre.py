from typing import Optional, List
from functools import lru_cache

from fastapi import Depends
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from db.elastic import get_elastic
from db.redis import get_redis

from models.genre import GenreDetail, Genre


class GenreService:

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis):
        self.elastic = elastic
        self.redis = redis

    async def get_genre_by_id(self, genre_id: str) -> Optional[GenreDetail]:
        return await self._get_genre_from_elastic_by_id(genre_id=genre_id)

    async def _get_genre_from_elastic_by_id(self, genre_id: str) -> Optional[GenreDetail]:
        try:
            doc = await self.elastic.get("genres", genre_id)
        except NotFoundError:
            return None
        return GenreDetail(**doc["_source"])

    async def get_genre_list(self) -> List[Genre]:
        genres_from_es = await self.elastic.search(index="genres")
        return list(map(lambda x: Genre(**x["_source"]), genres_from_es["hits"]["hits"]))


@lru_cache
def get_genre_service(elastic: AsyncElasticsearch = Depends(get_elastic),
                      redis: Redis = Depends(get_redis)) -> GenreService:
    return GenreService(elastic=elastic, redis=redis)
