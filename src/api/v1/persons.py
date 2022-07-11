from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.person import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    id: str
    full_name: str


@router.get("/{genre_uuid}", response_model=Person)
async def get_person_by_id(person_uuid: str, person_service: PersonService = Depends(get_person_service)):
    person_info = await person_service.get_person_by_id(person_uuid)
    if not person_info:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Such genre not found")
    return Person(id=person_info.id, name=person_info.full_name)


@router.get("/", response_model=List[Person])
async def get_person_list(person_service: PersonService = Depends(get_person_service)):
    person_list = await person_service.get_persons_list()
    return list(map(lambda x: Person(id=x.id, name=x.full_name), person_list))
