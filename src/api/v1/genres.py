from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from api.v1.messages import GENRE_NOT_FOUND_MESSAGE
from api.v1.schemas import GenreDetail, GenreInList
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get("/{genre_uuid}", response_model=GenreDetail, summary="Get info about genre")
async def get_genre_by_id(
    genre_uuid: str, genre_service: GenreService = Depends(get_genre_service),
):
    genre_info = await genre_service.get_genre_by_id(genre_uuid)
    if not genre_info:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=GENRE_NOT_FOUND_MESSAGE,
        )
    return GenreDetail(
        id=genre_info.id, name=genre_info.name, description=genre_info.description,
    )


@router.get("/", response_model=List[GenreInList], summary="Get genres list")
async def get_genre_list(genre_service: GenreService = Depends(get_genre_service)):
    genre_list = await genre_service.get_genre_list()
    return [GenreInList(id=x.id, name=x.name) for x in genre_list]
