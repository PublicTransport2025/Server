from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.users import User
from src.utils.security import verify_password, create_tokens

def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.login == email).one_or_none()
    if not user or not user.hash_pass:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if not verify_password(password, user.hash_pass):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return user

def login_user(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)
    access, refresh, expires_in = create_tokens(str(user.id))
    return {"access_token": access, "refresh_token": refresh, "expires_in": expires_in}
