from functools import lru_cache
from fastapi import Depends

from src.db.cache import AbstractCache, get_cache_refresh
from src.core import security
from src.core.config import REFRESH_TOKEN_EXPIRE_MINUTES
from src.services import ServiceCache

REFRESH_TOKEN_EXPIRE_SECONDS = REFRESH_TOKEN_EXPIRE_MINUTES * 60


class RefreshService(ServiceCache):
    def save_token(self, user_id: int, token: str):
        """Сохраняем активный рефреш токен"""
        token_id = security.decode_refresh_token(token).get('jti')
        if token_id:
            self.cache.sadd(f"{user_id}", token_id)

    def check_refresh_token(self, user_id: int, token: str):
        """Проверяем есть ли нужный токен в списке"""
        cached_tokens = self.cache.smembers(name=f"{user_id}")
        if token in cached_tokens:
            return True
        else:
            return False

    def remove_refresh_token(self, user_id: int, token: str):
        """Удаляем рефреш токен при выходе"""
        self.cache.srem(f'{user_id}', token)

    def remove_all_refresh_token(self, user_id: int):
        """Удаляем все рефреш токены при выходе со всех устройств"""
        cached_tokens = self.cache.smembers(name=f"{user_id}")
        for token in cached_tokens:
            self.cache.srem(f'{user_id}', token)


@lru_cache()
def get_refresh_service(
        cache: AbstractCache = Depends(get_cache_refresh),
) -> RefreshService:
    return RefreshService(cache=cache)
