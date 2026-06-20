import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings

if settings.database_url.startswith("sqlite"):
    sqlite_path = settings.database_url.replace("sqlite://", "")
    sqlite_dir = os.path.dirname(sqlite_path)
    if sqlite_dir and not os.path.exists(sqlite_dir):
        os.makedirs(sqlite_dir, exist_ok=True)

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def init_db():
    from backend.db import models
    Base.metadata.create_all(bind=engine)
