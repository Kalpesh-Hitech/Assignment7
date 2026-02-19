from fastapi import HTTPException

from config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
if settings.DATABASE_URL is None:
    raise HTTPException(status_code=404,detail="url is not fine")
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()