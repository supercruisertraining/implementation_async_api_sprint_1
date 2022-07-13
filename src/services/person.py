from typing import Optional, List
from functools import lru_cache

from fastapi import Depends
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person


class PersonService:

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis):
        self.elastic = elastic
        self.redis = redis

    async def get_person_by_id(self, person_id: str) -> Optional[Person]:
        return await self._get_person_from_elastic_by_id(person_id=person_id)

    async def _get_person_from_elastic_by_id(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get("persons", person_id)
        except NotFoundError:
            return None
        return Person(**doc["_source"])

    async def get_persons_list(self, page_number: int, page_size: int, sort_rule: Optional[dict]) -> List[Person]:
        query_body = {}
        query_body.update({"size": page_size, "from": (page_number - 1) * page_size})
        if sort_rule:
            query_body.update({
                "sort": {f'{sort_rule["field"]}.raw'
                         if sort_rule["field"] in ("full_name",)
                         else sort_rule["field"]: {"order": "desc" if sort_rule["desc"] else "asc"}}
            })

        persons_from_es = await self.elastic.search(index="persons", body=query_body)
        return list(map(lambda x: Person(**x["_source"]), persons_from_es["hits"]["hits"]))


@lru_cache
def get_person_service(elastic: AsyncElasticsearch = Depends(get_elastic),
                       redis: Redis = Depends(get_redis)) -> PersonService:
    return PersonService(elastic=elastic, redis=redis)
