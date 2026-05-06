from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# The engine is the actual connection to the database
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite-only setting
)

# A session is like a "unit of work" — you open one, do queries, then close it
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All your models will inherit from this Base
class Base(DeclarativeBase):
    pass