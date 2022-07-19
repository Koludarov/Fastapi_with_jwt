from sqlmodel import Session, create_engine
import databases
from sqlalchemy import create_engine as cr
from sqlalchemy import MetaData

from src.core import config

__all__ = ("get_session", "database", "metadata", "engine1")

database = databases.Database(config.DATABASE_URL)
metadata = MetaData()
engine1 = cr(
    config.DATABASE_URL
)

engine = create_engine(config.DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
