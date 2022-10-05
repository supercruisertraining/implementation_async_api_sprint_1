from pydantic import BaseModel
from typing import List
import datetime

from utils.schemas import BaseOrjsonModel


class GenreInFilmDetail(BaseOrjsonModel):
    id: str
    name: str


class PersonInFilmDetail(BaseOrjsonModel):
    id: str
    full_name: str


class FilmDetail(BaseOrjsonModel):
    id: str
    title: str
    rating: float
    description: str
    creation_date: datetime.date
    genres: List[GenreInFilmDetail]

    actors: List[PersonInFilmDetail]
    writers: List[PersonInFilmDetail]
    directors: List[PersonInFilmDetail]


class FilmInList(BaseOrjsonModel):
    id: str
    title: str
    rating: float


class FilmInListExtended(BaseOrjsonModel):
    id: str
    title: str
    rating: float
    description: str


class GenreDetail(BaseOrjsonModel):
    id: str
    name: str
    description: str


class GenreInList(BaseOrjsonModel):
    id: str
    name: str


class Person(BaseOrjsonModel):
    id: str
    full_name: str
