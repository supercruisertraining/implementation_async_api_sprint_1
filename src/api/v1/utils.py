from dataclasses import dataclass

from fastapi import Query


@dataclass
class PaginatedParams:
    page_number: int
    page_size: int


async def paging_parameters(page_number: int = Query(default=1, alias="page[number]", ge=1),
                            page_size: int = Query(default=50, alias="page[size]", ge=1)) -> PaginatedParams:
    return PaginatedParams(page_number=page_number, page_size=page_size)
