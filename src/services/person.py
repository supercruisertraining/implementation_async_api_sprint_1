import json
from typing import Optional, List
from functools import lru_cache

from fastapi import Depends

from models.person import Person
from services.cache import AbstractCache, get_cache
from services.storage import AbstractStorage, get_storage
from core.config import config

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    name = config.es_persons_index

    def __init__(self, cache: AbstractCache, storage: AbstractStorage):
        self.storage = storage
        self.cache = cache

    async def get_person_by_id(self, person_id: str) -> Optional[Person]:
        person_data = await self.cache.get_from_cache(person_id)
        if not person_data:
            person_data = await self.storage.get_object_by_id(index=self.name, object_id=person_id)
            if person_data:
                await self.cache.put_to_cache(key=person_id, value=json.dumps(person_data))
            else:
                return None
        return Person(**person_data)

    async def get_persons_list(self, page_number: int, page_size: int, sort_rule: Optional[dict]) -> List[Person]:
        query_body = {}
        query_body.update({"size": page_size, "from": (page_number - 1) * page_size})
        if sort_rule:
            query_body.update({
                "sort": {f'{sort_rule["field"]}.raw'
                         if sort_rule["field"] in ("full_name",)
                         else sort_rule["field"]: {"order": "desc" if sort_rule["desc"] else "asc"}}
            })
        person_list = await self.cache.get_from_cache(self.cache.cook_cache_key(self.name, page_number,
                                                                                page_size, sort_rule))
        if not person_list:
            person_list = await self.storage.get_object_list(index=self.name, query=json.dumps(query_body))
            if person_list:
                await self.cache.put_to_cache(self.cache.cook_cache_key(self.name, page_number, page_size, sort_rule),
                                              value=json.dumps(person_list))
            else:
                return []
        return list(map(lambda x: Person(**x), person_list))


@lru_cache
def get_person_service(storage: AbstractStorage = Depends(get_storage),
                       cache: AbstractCache = Depends(get_cache)) -> PersonService:
    return PersonService(storage=storage, cache=cache)
