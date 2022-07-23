from utils.schemas import BaseOrjsonModel


class Person(BaseOrjsonModel):
    id: str
    full_name: str
