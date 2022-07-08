import datetime
from http import HTTPStatus
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Query
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
    rating: float
    description: str
    creation_date: datetime.date
    genres: List[GenreInFilmDetail]

    actors: List[PersonInFilmDetail]
    writers: List[PersonInFilmDetail]
    directors: List[PersonInFilmDetail]


class FilmInList(BaseModel):
    id: str
    title: str
    rating: float


@router.get('/{film_uuid}', response_model=FilmDetail)
async def film_details(film_uuid: str, film_service: FilmService = Depends(get_film_service)) -> FilmDetail:
    film = await film_service.get_by_id(film_uuid)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return FilmDetail(id=film.id,
                      title=film.title,
                      rating=film.rating,
                      description=film.description,
                      creation_date=film.creation_date,
                      genres=film.genres,
                      actors=film.actors,
                      writers=film.writers,
                      directors=film.directors
                      )


@router.get("/", response_model=List[FilmInList])
async def get_film_list(film_service: FilmService = Depends(get_film_service),
                        page_number: int = Query(default=1, alias="page[number]"),
                        page_size: int = Query(default=50, alias="page[size]"),
                        filter_genre: Union[List[str], None] = Query(default=None, alias="filter[genre]"),
                        sort: str = Query(default=None)):
    sort_desc = None
    if sort:
        if str(sort).startswith("-"):
            sort_desc = sort
            sort = None
    filters_should = None
    if filter_genre:
        filters_should = {"genres": filter_genre}
    films = await film_service.get_film_list(sort=sort, sort_desc=sort_desc, filters_should=filters_should)
    return list(map(lambda x: FilmInList(id=x.id, title=x.title, rating=x.rating), films))
