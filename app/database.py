from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
# Database URL
import os

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

# Engine
engine = create_engine(DB_URL)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base (used by models and Alembic)
Base = declarative_base()

# Dependency for FastAPI or other apps
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()