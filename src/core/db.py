from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.core.constants import DB_NAME, DB_HOST, DB_PORT, DB_USER, DB_PASS

db_name = DB_NAME
db_host = DB_HOST
db_port = DB_PORT
db_user = DB_USER
db_pass = DB_PASS


class Base(DeclarativeBase):
    pass


engine_sync = create_engine(f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
SessionLocal = sessionmaker(bind=engine_sync, expire_on_commit=False)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_client = Depends(get_session)

engine = create_async_engine(f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session():
    async with async_session_maker() as session:
        yield session


db_async_client = Depends(get_async_session)
