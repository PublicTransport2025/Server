from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    code: str


class UserResetPass(BaseModel):
    email: EmailStr
    password: str
    code: str
