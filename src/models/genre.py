from pydantic import BaseModel


class GenreDetail(BaseModel):
    id: str
    name: str
    description: str


class Genre(BaseModel):
    id: str
    name: str
