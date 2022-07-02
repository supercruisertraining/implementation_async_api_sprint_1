import orjson
import datetime
from typing import List

# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class PersonInFilm(BaseModel):
    id: str
    full_name: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class GenreInFilm(BaseModel):
    id: str
    name: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Film(BaseModel):
    id: str
    title: str
    description: str
    rating: float
    creation_date: datetime.date

    genres: List[GenreInFilm]

    actors: List[PersonInFilm]
    writers: List[PersonInFilm]
    directors: List[PersonInFilm]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
