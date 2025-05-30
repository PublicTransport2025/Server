from pydantic import BaseModel, EmailStr


class FeedbackWrited(BaseModel):
    name: str
    email: EmailStr
    mark: int
    about: str
