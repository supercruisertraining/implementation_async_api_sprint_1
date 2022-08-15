import json
from typing import Optional, List
from functools import lru_cache

from fastapi import Depends
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    name = "persons"

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis):
        self.elastic = elastic
        self.redis = redis

    async def get_person_by_id(self, person_id: str) -> Optional[Person]:
        person_data = await self._person_from_cache(person_id)
        if not person_data:
            person_data = await self._get_person_from_elastic_by_id(person_id=person_id)
            if person_data:
                await self._put_data_to_cache(field=person_id, value=person_data.json())
        return person_data

    async def _get_person_from_elastic_by_id(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get("persons", person_id)
        except NotFoundError:
            return None
        return Person(**doc["_source"])

    async def _get_person_list_from_elastic(self, page_number: int, page_size: int,
                                            sort_rule: Optional[dict]) -> List[Person]:
        query_body = {}
        query_body.update({"size": page_size, "from": (page_number - 1) * page_size})
        if sort_rule:
            query_body.update({
                "sort": {f'{sort_rule["field"]}.raw'
                         if sort_rule["field"] in ("full_name",)
                         else sort_rule["field"]: {"order": "desc" if sort_rule["desc"] else "asc"}}
            })
        try:
            persons_from_es = await self.elastic.search(index=self.name, body=query_body)
        except NotFoundError:
            return []
        return list(map(lambda x: Person(**x["_source"]), persons_from_es["hits"]["hits"]))

    async def get_persons_list(self, page_number: int, page_size: int, sort_rule: Optional[dict]) -> List[Person]:
        cache_key = self._cook_cache_key(page_number, page_size, sort_rule)
        person_list = await self._get_person_list_from_cache(cache_key)
        if not person_list:
            person_list = await self._get_person_list_from_elastic(page_number, page_size, sort_rule)
            if person_list:
                await self._put_data_to_cache(field=cache_key, value=json.dumps([x.json() for x in person_list]))
        return person_list

    async def _put_data_to_cache(self, field: str, value: str):
        await self.redis.set(key=field, value=value, expire=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        person_data_raw = await self.redis.get(person_id)
        if not person_data_raw:
            return None
        return Person.parse_raw(person_data_raw)

    async def _get_person_list_from_cache(self, key: str) -> List[Person]:
        person_list_raw = await self.redis.get(key)
        if not person_list_raw:
            return []
        return list(map(lambda x: Person.parse_raw(x), json.loads(person_list_raw)))

    def _cook_cache_key(self, page_number: int, page_size: int, sort_rule: Optional[dict]) -> str:
        source_dict = {"page_number": page_number, "page_size": page_size}
        if isinstance(sort_rule, dict):
            for key in sort_rule.keys():
                source_dict.update({key: sort_rule[key]})
        source_dict_keys = list(source_dict.keys())
        source_dict_keys.sort()
        return f"{self.name}::" + "::".join(f"{key}:{source_dict[key]}" for key in source_dict_keys)


@lru_cache
def get_person_service(elastic: AsyncElasticsearch = Depends(get_elastic),
                       redis: Redis = Depends(get_redis)) -> PersonService:
    return PersonService(elastic=elastic, redis=redis)
