from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import timedelta, datetime
from dotenv import load_dotenv
import os

env = load_dotenv()

# SQLite used for simplicity; in production use PostgreSQL or MySQL
DATABASE_URL = "sqlite:///./lms.db"

# Create engine (used to connect to the DB)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal is a factory for DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

ACCESSTOKEN_EXPIRED_TIME = timedelta(minutes=20)
REFRESHTOKEN_EXPIRED_TIME = timedelta(days=1)