from pydantic import BaseModel


class NameUpd(BaseModel):
    name: str