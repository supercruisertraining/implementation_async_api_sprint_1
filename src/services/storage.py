from abc import ABC, abstractmethod
from typing import List, Optional
from functools import lru_cache

from fastapi import Depends
from elasticsearch import AsyncElasticsearch, NotFoundError

from db.elastic import get_elastic


class AbstractStorage(ABC):

    @abstractmethod
    async def get_object_by_id(self, index: str, object_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def get_object_list(self, index: str, query: Optional[str] = None) -> Optional[List[dict]]:
        pass


class ElasticSearchStorage(AbstractStorage):

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_object_by_id(self, index: str, object_id: str) -> Optional[dict]:
        try:
            data = await self.elastic.get(index=index, id=object_id)
        except NotFoundError:
            return None
        return data["_source"]

    async def get_object_list(self, index: str, query: Optional[str] = None) -> Optional[List[dict]]:
        try:
            data = await self.elastic.search(index=index, body=query)
        except NotFoundError:
            return []
        return list(map(lambda x: x["_source"], data["hits"]["hits"]))


@lru_cache
def get_storage(elastic: AsyncElasticsearch = Depends(get_elastic)):
    return ElasticSearchStorage(elastic)
