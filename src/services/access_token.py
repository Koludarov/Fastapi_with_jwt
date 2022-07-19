from functools import lru_cache
from fastapi import Depends
from typing import Optional

from src.db.cache import AbstractCache, get_cache_access
from src.core import security
from src.services import ServiceCache


class AccessService(ServiceCache):
    def get_token(self, token_id: str) -> Optional[str]:
        """Ищем токен в блек листе."""
        if cached_token := self.cache.get(key=f"{token_id}"):
            return cached_token

    def save_token(self, token: str):
        """Добавляем токен в блек лист"""
        token_id = security.decode_access_token(token).get('jti')
        if token_id:
            self.cache.set(key=f"{token_id}", value='blocked', nx=True)


@lru_cache()
def get_access_service(
    cache: AbstractCache = Depends(get_cache_access),
) -> AccessService:
    return AccessService(cache=cache)
