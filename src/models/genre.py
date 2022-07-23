from pydantic import BaseModel

from utils.schemas import BaseOrjsonModel


class GenreDetail(BaseOrjsonModel):
    id: str
    name: str
    description: str


class Genre(BaseOrjsonModel):
    id: str
    name: str
