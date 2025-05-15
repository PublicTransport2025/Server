from datetime import datetime
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int 

class TokenPayload(BaseModel):
    sub: str
    exp: datetime
