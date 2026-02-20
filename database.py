from fastapi import HTTPException

from config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker,create_async_engine
if settings.ASYNC_DATABASE_URL is None:
    raise HTTPException(status_code=404,detail="url is not fine")
asyncengine = create_async_engine(settings.ASYNC_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=asyncengine)
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

async def async_get_db():
    # db = SessionLocal()
    # try:
    #     yield db
    # finally:
    #     db.close()
    async with AsyncSessionLocal() as db:
        yield db

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()