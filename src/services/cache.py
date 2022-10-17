# coding=utf-8
import json

from fastapi import Depends
from abc import ABC, abstractmethod
from typing import Union, List, Optional
from functools import lru_cache

from aioredis import Redis
from db.redis import get_redis


class AbstractCache(ABC):
    @abstractmethod
    async def get_from_cache(self, key: str) -> Optional[Union[List, dict]]:
        pass

    @abstractmethod
    async def put_to_cache(self, key: str, value: str):
        pass

    @abstractmethod
    def cook_cache_key(self, *args) -> str:
        pass


class RedisCache(AbstractCache):

    FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_from_cache(self, key: str):
        data_raw = await self.redis.get(key)
        if not data_raw:
            return None
        try:
            return json.loads(data_raw)
        except json.decoder.JSONDecodeError:
            return None

    async def put_to_cache(self, key: str, value: str):
        await self.redis.set(key, value, ex=self.FILM_CACHE_EXPIRE_IN_SECONDS)

    def cook_cache_key(self, *args):
        return "::".join(map(str, args))


@lru_cache
def get_cache(redis: Redis = Depends(get_redis)) -> AbstractCache:
    return RedisCache(redis)

