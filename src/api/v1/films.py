import datetime
from http import HTTPStatus
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Query

from services.film import FilmService, get_film_service
from api.v1.schemas import FilmDetail, FilmInList

router = APIRouter()


@router.get('/{film_uuid}', response_model=FilmDetail)
async def film_details(film_uuid: str, film_service: FilmService = Depends(get_film_service)) -> FilmDetail:
    film = await film_service.get_by_id(film_uuid)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return FilmDetail(**film.dict())


@router.get("/", response_model=List[FilmInList])
async def get_film_list(film_service: FilmService = Depends(get_film_service),
                        page_number: int = Query(default=1, alias="page[number]"),
                        page_size: int = Query(default=50, alias="page[size]"),
                        filter_genre: Union[List[str], None] = Query(default=None, alias="filter[genre]"),
                        sort: str = Query(default=None)):
    sort_rule = None
    if sort:
        if str(sort).startswith("-"):
            sort_rule = {"field": sort[1:], "desc": True}
        else:
            sort_rule = {"field": sort, "desc": False}
    filters_should = None
    if filter_genre:
        filters_should = {"genres": filter_genre}
    films = await film_service.get_film_list(page_size=page_size, page_number=page_number,
                                             sort_rule=sort_rule,  filters_should=filters_should)
    return list(map(lambda x: FilmInList(id=x.id, title=x.title, rating=x.rating), films))
