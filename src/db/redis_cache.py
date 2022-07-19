from typing import NoReturn, Optional, Union

from src.db import AbstractCache

__all__ = ("CacheRedis",)


class CacheRedis(AbstractCache):
    def get(self, key: str) -> Optional[dict]:
        return self.cache.get(name=key)

    def set(
        self,
        key: str,
        value: Union[bytes, str],
        expire: int = None,
        nx: bool = False,
    ):
        self.cache.set(name=key, value=value, ex=expire)

    def sadd(self, name: str, *values):
        self.cache.sadd(name, *values)

    def smembers(self, name: str):
        return self.cache.smembers(name=name)

    def srem(self, name: str, *values):
        self.cache.srem(name, *values)

    def close(self) -> NoReturn:
        self.cache.close()
