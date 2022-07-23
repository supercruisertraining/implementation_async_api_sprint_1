import datetime
from typing import List

from utils.schemas import BaseOrjsonModel


class PersonInFilm(BaseOrjsonModel):
    id: str
    full_name: str


class GenreInFilm(BaseOrjsonModel):
    id: str
    name: str


class Film(BaseOrjsonModel):
    id: str
    title: str
    description: str
    rating: float
    creation_date: datetime.date

    genres: List[GenreInFilm]

    actors: List[PersonInFilm]
    writers: List[PersonInFilm]
    directors: List[PersonInFilm]
