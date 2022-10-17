from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Query

from services.film import FilmService, get_film_service
from api.v1.schemas import FilmDetail, FilmInList, FilmInListExtended
from api.v1.messages import FILM_NOT_FOUND_MESSAGE
from api.v1.utils import paging_parameters

router = APIRouter()


@router.get('/{film_uuid}', response_model=FilmDetail, summary="Get film detail info")
async def film_details(film_uuid: str, film_service: FilmService = Depends(get_film_service)) -> FilmDetail:
    film = await film_service.get_by_id(film_uuid)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND_MESSAGE)
    return FilmDetail(**film.dict())


@router.get("/", response_model=list[FilmInList], summary="Get films list")
async def get_film_list(film_service: FilmService = Depends(get_film_service),
                        paginated_params=Depends(paging_parameters),
                        filter_genre: Union[list[str], None] = Query(default=None, alias="filter[genre]"),
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
    films = await film_service.get_film_list(page_size=paginated_params.page_size,
                                             page_number=paginated_params.page_number,
                                             sort_rule=sort_rule,
                                             filters_should=filters_should)
    return list(map(lambda x: FilmInList(id=x.id, title=x.title, rating=x.rating), films))


@router.get("/search/", response_model=list[FilmInListExtended], summary="Search films by query")
async def search_in_films(query: str,
                          film_service: FilmService = Depends(get_film_service),
                          paginated_params=Depends(paging_parameters),
                          ):
    films = await film_service.search_films(search_query=query,
                                            page_size=paginated_params.page_size,
                                            page_number=paginated_params.page_number)
    return list(map(lambda x: FilmInListExtended(id=x.id, title=x.title, rating=x.rating, description=x.description),
                    films))
