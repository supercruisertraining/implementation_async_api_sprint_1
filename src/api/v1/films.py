import uuid
import datetime
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.film import FilmService, get_film_service

router = APIRouter()


class GenreInFilmDetail(BaseModel):
    id: str
    name: str


class PersonInFilmDetail(BaseModel):
    id: str
    full_name: str


class FilmDetail(BaseModel):
    id: str
    title: str
    description: str
    creation_date: datetime.date
    genres: List[GenreInFilmDetail]

    actors: List[PersonInFilmDetail]
    writers: List[PersonInFilmDetail]
    directors: List[PersonInFilmDetail]


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_uuid}', response_model=FilmDetail)
async def film_details(film_uuid: str, film_service: FilmService = Depends(get_film_service)) -> FilmDetail:
    film = await film_service.get_by_id(film_uuid)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return FilmDetail(id=film.id,
                      title=film.title,
                      description=film.description,
                      creation_date=film.creation_date,
                      genres=film.genres,
                      actors=film.actors,
                      writers=film.writers,
                      directors=film.directors
                      )
