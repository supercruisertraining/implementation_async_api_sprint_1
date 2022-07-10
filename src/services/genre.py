from typing import Optional
from functools import lru_cache

from fastapi import Depends
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from db.elastic import get_elastic
from db.redis import get_redis

from models.genre import Genre


class GenreService:

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis):
        self.elastic = elastic
        self.redis = redis

    async def get_genre_by_id(self, genre_id: str) -> Optional[Genre]:
        return await self._get_genre_from_elastic_by_id(genre_id=genre_id)

    async def _get_genre_from_elastic_by_id(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get("genres", genre_id)
        except NotFoundError:
            return None
        return Genre(**doc["_source"])


@lru_cache
def get_genre_service(elastic: AsyncElasticsearch = Depends(get_elastic),
                      redis: Redis = Depends(get_redis)) -> GenreService:
    return GenreService(elastic=elastic, redis=redis)
