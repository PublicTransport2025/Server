from pydantic import BaseModel


class AtpInput(BaseModel):
    title: str
    numbers: str
    about: str
    phone: str
    report: str


class AtpModel(AtpInput):
    id: int
