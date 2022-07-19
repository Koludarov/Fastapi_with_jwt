from abc import ABC, abstractmethod
from typing import Optional, Union

__all__ = (
    "AbstractCache",
    "get_cache",
    "get_cache_access",
    "get_cache_refresh",
)

from src.core import config


class AbstractCache(ABC):
    def __init__(self, cache_instance):
        self.cache = cache_instance

    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def set(
        self,
        key: str,
        value: Union[bytes, str],
        expire: int = config.CACHE_EXPIRE_IN_SECONDS,
        nx: bool = False,
    ):
        pass

    @abstractmethod
    def sadd(self, name: str, *values):
        pass

    @abstractmethod
    def smembers(self, name: str):
        pass

    @abstractmethod
    def srem(self, name: str, *values):
        pass

    @abstractmethod
    def close(self):
        pass


cache: Optional[AbstractCache] = None
cache1: Optional[AbstractCache] = None
cache2: Optional[AbstractCache] = None


# Функция понадобится при внедрении зависимостей
def get_cache() -> AbstractCache:
    return cache


def get_cache_access() -> AbstractCache:
    return cache1


def get_cache_refresh() -> AbstractCache:
    return cache2
