from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.genre import GenreService, get_genre_service

router = APIRouter()


class GenreDetail(BaseModel):
    id: str
    name: str
    description: str


class GenreInList(BaseModel):
    id: str
    name: str


@router.get("/{genre_uuid}", response_model=GenreDetail)
async def get_genre_by_id(genre_uuid: str, genre_service: GenreService = Depends(get_genre_service)):
    genre_info = await genre_service.get_genre_by_id(genre_uuid)
    if not genre_info:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Such genre not found")
    return GenreDetail(id=genre_info.id, name=genre_info.name, description=genre_info.description)


@router.get("/", response_model=List[GenreInList])
async def get_genre_list(genre_service: GenreService = Depends(get_genre_service)):
    genre_list = await genre_service.get_genre_list()
    return list(map(lambda x: GenreInList(id=x.id, name=x.name), genre_list))
