from sqlmodel import Session

from databases import Database

from src.db import AbstractCache


class ServiceMixin:
    def __init__(self, cache: AbstractCache, session: Session):
        self.cache: AbstractCache = cache
        self.session: Session = session


class ServiceCache:
    def __init__(self, cache: AbstractCache):
        self.cache: AbstractCache = cache


class ServiceBase:
    def __init__(self, database: Database):
        self.database = database
