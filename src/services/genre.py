import json
from typing import Optional
from functools import lru_cache

from fastapi import Depends

from services.cache import AbstractCache, get_cache
from services.storage import AbstractStorage, get_storage
from models.genre import GenreDetail, Genre
from core.config import config


GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService:
    name = config.es_genres_index

    def __init__(self, cache: AbstractCache, storage: AbstractStorage):
        self.storage = storage
        self.cache = cache

    async def get_genre_by_id(self, genre_id: str) -> Optional[GenreDetail]:
        genre_data = await self.cache.get_from_cache(genre_id)
        if not genre_data:
            genre_data = await self.storage.get_object_by_id(index=self.name, object_id=genre_id)
            if genre_data:
                await self.cache.put_to_cache(key=genre_id, value=json.dumps(genre_data))
            else:
                return None
        return GenreDetail(**genre_data)

    async def get_genre_list(self) -> list[Genre]:
        genres_list = await self.cache.get_from_cache(key=self.name)
        if not genres_list:
            genres_list = await self.storage.get_object_list(index=self.name)
            if genres_list:
                await self.cache.put_to_cache(key=self.name, value=json.dumps(genres_list))
            else:
                return []
        return list(map(lambda x: Genre(**x), genres_list))


@lru_cache
def get_genre_service(storage: AbstractStorage = Depends(get_storage),
                      cache: AbstractCache = Depends(get_cache)) -> GenreService:
    return GenreService(storage=storage, cache=cache)
