from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from services.person import PersonService, get_person_service
from api.v1.schemas import Person
from api.v1.messages import PERSON_NOT_FOUND_MESSAGE
from api.v1.utils import paging_parameters

router = APIRouter()


@router.get("/{person_uuid}", response_model=Person, summary="Get person info")
async def get_person_by_id(person_uuid: str, person_service: PersonService = Depends(get_person_service)):
    person_info = await person_service.get_person_by_id(person_uuid)
    if not person_info:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND_MESSAGE)
    return Person(id=person_info.id, full_name=person_info.full_name)


@router.get("/", response_model=List[Person], summary="Get persons list")
async def get_person_list(person_service: PersonService = Depends(get_person_service),
                          sort: str = Query(default=None),
                          paginated_params=Depends(paging_parameters),
                          ):
    sort_rule = None
    if sort:
        if str(sort).startswith("-"):
            sort_rule = {"field": sort[1:], "desc": True}
        else:
            sort_rule = {"field": sort, "desc": False}
    person_list = await person_service.get_persons_list(page_number=paginated_params.page_number,
                                                        page_size=paginated_params.page_size,
                                                        sort_rule=sort_rule)
    return list(map(lambda x: Person(id=x.id, full_name=x.full_name), person_list))
